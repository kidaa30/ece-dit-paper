from heapq import heapify, heappop, heappush
import pdb

from Model.CPU import CPU
from Model import algorithms
from Model.Job import Job
import Drawer


def heappeek(heap):
    return heap[0] if len(heap) > 0 else None


class Simulator(object):  # Global FJP only
    def __init__(self, tau, stop, nbrCPUs, scheduler, abortAndRestart, verbose=False):
        """stop can be set to None for default value"""
        self.verbose = verbose
        self.system = tau
        self.m = nbrCPUs
        self.AR = abortAndRestart
        if stop is None:
            fpdit = algorithms.findFirstDIT(tau)
            if fpdit:
                stop = fpdit + tau.hyperPeriod()
            else:
                stop = tau.omax() + tau.hyperPeriod()
        self.stop = stop + 1  # I just solved every OBOE in the world

        # CPUs are accessible via either
        # - CPUs : a list with fixed ordering
        # - activeCPUsHeap and preemptedCPUs : where the ordering is not guaranteed
        self.CPUs = [CPU() for i in range(self.m)]
        self.activeCPUsHeap = []
        heapify(self.activeCPUsHeap)
        for cpu in self.CPUs:
            heappush(self.activeCPUsHeap, cpu)
        self.preemptedCPUs = set()

        self.scheduler = scheduler

        self.t = -1
        self.deadlineMisses = []
        self.activeJobsHeap = []
        heapify(self.activeJobsHeap)

        self.drawer = Drawer.Drawer(self, stop)

    def activateCPUs(self):
    # move active CPU from preemptedCPUs to activeCPUsHeap
        cpuToActivate = []
        for cpu in self.preemptedCPUs:
            if cpu.preemptionTimeLeft == 0:
                cpuToActivate.append(cpu)
        for cpu in cpuToActivate:
            self.preemptedCPUs.remove(cpu)
            heappush(self.activeCPUsHeap, cpu)

    def getCurrentJobs(self, getWaitingJobs=True, getBusyJobs=True):
        waitingJobs = []
        busyJobs = []
        if getWaitingJobs:
            waitingJobs = [job for prio, job in self.activeJobsHeap]
        if getBusyJobs:
            busyJobs = filter(None, [cpu.job for cpu in self.CPUs])
        return waitingJobs + busyJobs

    def updatePriorities(self, job="all"):
        jobs = []
        if job == "all":
            jobs.extend(self.getCurrentJobs())
        else:
            jobs.append(job)
        for job in jobs:
            job.priority = self.scheduler.priority(job, self)
            if self.verbose:
                print "\t\tpriority of ", job, "is now", job.priority

    def updateHeaps(self):
        # possible bottleneck
        newJobHeap = []
        for prio, job in self.activeJobsHeap:
            newJobHeap.append((-1 * job.priority, job))
        self.activeJobsHeap = newJobHeap
        heapify(self.activeCPUsHeap)
        heapify(self.activeJobsHeap)

    def mostPrioritaryJob(self):
        return heappeek(self.activeJobsHeap)[1] if len(self.activeJobsHeap) > 0 else None

    def lessPrioritaryCPU(self):
        return heappeek(self.activeCPUsHeap)

    def incrementTime(self):
        self.t += 1
        if self.verbose: print "t=", self.t
        # Initialize scheduler
        self.scheduler.initInstant()
        # remove finished job from CPUs
        self.activateCPUs()
        for cpu in self.activeCPUsHeap:
            if cpu.job and cpu.job.isFinished():
                if self.verbose:
                    print "\tCPU ", cpu, "is finished"
                cpu.job = None
        self.updatePriorities()
        self.updateHeaps()
        # check for deadline miss
        for job in self.getCurrentJobs():
            assert job
            if self.t >= job.deadline:
                assert job.computation < job.task.C
                self.deadlineMisses.append((self.t, job))
        # check for job arrival
        for task in self.system.tasks:
            if self.t >= task.O and self.t % task.T == task.O % task.T:
                newJob = Job(task, self.t)
                newJob.priority = self.scheduler.priority(newJob, self)
                if self.verbose: print "\tarrival of job", newJob
                heappush(self.activeJobsHeap, (-1 * newJob.priority, newJob))

        # preemptions
        while True:
            # update priorities
            self.updatePriorities()
            self.updateHeaps()
            # check for preemptions
            if self.verbose:
                print "\t", self.mostPrioritaryJob(), "(", str(self.mostPrioritaryJob().priority if self.mostPrioritaryJob() else None), ") vs.", self.lessPrioritaryCPU(), "(", str(self.lessPrioritaryCPU().priority() if self.lessPrioritaryCPU() else None), ")"
            if self.mostPrioritaryJob() and self.lessPrioritaryCPU() and self.mostPrioritaryJob().priority >= self.lessPrioritaryCPU().priority():
                # special case of equal priorities : decided by the scheduler
                if self.mostPrioritaryJob().priority == self.lessPrioritaryCPU().priority():
                    if self.verbose:
                        print "equal priority: preemption policy of scheduler :", self.scheduler.preemptEqualPriorities()
                    if not self.scheduler.preemptEqualPriorities():
                        break
                if self.verbose:
                    print "\tpremption!"
                preemptiveJob = heappop(self.activeJobsHeap)[1]
                preemptedCPU = heappop(self.activeCPUsHeap)
                preemptedJob = preemptedCPU.job  # may be None

                # assign preemptive job to the CPU and push CPU in the correct heap
                self.updatePriorities(job=preemptiveJob)
                preemptedCPU.job = preemptiveJob
                if preemptiveJob.preempted:
                    preemptiveJob.preempted = False
                    preemptedCPU.preemptionTimeLeft = preemptiveJob.alpha()
                    self.preemptedCPUs.add(preemptedCPU)
                else:
                    heappush(self.activeCPUsHeap, preemptedCPU)

                # put the preempted job back in the active job heap
                if preemptedJob:
                    preemptedJob.preempted = True
                    if self.AR:
                        preemptedJob.computation = 0
                        self.drawer.drawAbort(preemptedJob.task, self.t)
                    heappush(self.activeJobsHeap, (-1 * preemptedJob.priority, preemptedJob))

                if self.verbose:
                    print "\t", self.mostPrioritaryJob(), "(", str(self.mostPrioritaryJob().priority if self.mostPrioritaryJob() else None), ") vs.", self.lessPrioritaryCPU(), "(", str(self.lessPrioritaryCPU().priority() if self.lessPrioritaryCPU() else None), ")"
            else:
                break
        # activate CPUs whose preemption is finished
        self.activateCPUs()
        # compute tasks in active CPU
        for cpu in self.activeCPUsHeap:
            if cpu.job:
                cpu.job.computation += 1
        # compute preemptions
        for cpu in self.preemptedCPUs:
            cpu.preemptionTimeLeft -= 1
        if self.verbose:
            for i, cpu in enumerate(self.CPUs):
                print "\t", i, cpu
                if cpu in self.preemptedCPUs:
                    print "\t(preempt)", cpu.preemptionTimeLeft, "left"

    def run(self, stopAtDeadlineMiss=True):
        while(self.t < self.stop):
            self.incrementTime()

            for miss in self.deadlineMisses:
                if self.verbose: print "DEADLINE MISS at t=", (miss[0] - 1), "for job", miss[1]
            if len(self.deadlineMisses) > 0:
                if stopAtDeadlineMiss:
                    break
            else:
                self.deadlineMisses = []
                self.drawer.drawInstant(self.t)
        self.drawer.drawArrivalsAndDeadlines()

    def success(self):
        assert self.t >= 0, "Simulator.success: call run() first"
        return self.t == self.stop
