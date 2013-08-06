from heapq import heapify, heappop, heappush
from Helper import ComparableMixin
from Model.Task import Task
from Model.CPU import CPU
from Scheduler import EDF
from Scheduler import RM
from Model.Job import Job
import Drawer


def heappeek(heap):
	if len(heap) == 0:
		return None
	return heap[0]


class Simulator(object):  # Global FJP only
	def __init__(self, tau, stop, preempTime, m, schedulerName, abortAndRestart):
		self.system = tau
		self.m = m
		self.alpha = preempTime
		self.AR = abortAndRestart
		self.stop = stop + 1  # I just solved every OBOE in the world

		# CPUs are accessible via either
		# - CPUs : a list with fixed ordering
		# - activeCPUsHeap and preemptedCPUs : where the ordering is not guaranteed
		self.CPUs = [CPU() for i in range(m)]
		self.activeCPUsHeap = []
		heapify(self.activeCPUsHeap)
		for cpu in self.CPUs:
			heappush(self.activeCPUsHeap, cpu)
		self.preemptedCPUs = set()

		if schedulerName == "EDF":
			self.scheduler = EDF(tau)
		elif schedulerName == "RM":
			self.scheduler = RM(tau)
		else:
			raise ValueError("schedulerName " + str(schedulerName) + " is unknown")

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

	def incrementTime(self, verbose=True):
		self.t += 1
		if verbose: print "t=", self.t
		# remove finished job from CPUs
		for cpu in self.activeCPUsHeap:
			if cpu.job and cpu.job.isFinished():
				cpu.job = None
		heapify(self.activeCPUsHeap)  # need to re-heapify after update
		# check for deadline miss
		for activeJobsTuple in self.activeJobsHeap + filter(lambda tupl: tupl[1] is not None, [(None, cpu.job) for cpu in self.CPUs]):
			job = activeJobsTuple[1]
			assert job, str(self.activeJobsHeap  + filter(lambda tupl: tupl[1] is not None, [(None, cpu.job) for cpu in self.CPUs]))
			if self.t > job.deadline:
				self.deadlineMisses.append((self.t, job))
		# check for job arrival
		for task in self.system.tasks:
			if self.t >= task.O and self.t % task.T == task.O % task.T:
				newJob = Job(task, self.t)
				if verbose: print "\tarrival of job:", newJob
				newJob.priority = self.scheduler.priority(newJob)
				heappush(self.activeJobsHeap, (-1 * newJob.priority, newJob))
		# preemptions
		mostPrioritaryJob = heappeek(self.activeJobsHeap)[1] if len(self.activeJobsHeap) > 0 else None
		lessPrioritaryCPU = heappeek(self.activeCPUsHeap)
		if verbose: print "\tactiveCPUsHeap (", ",".join([str(cpu) for cpu in self.activeCPUsHeap]), ")"
		if verbose: print "\t", mostPrioritaryJob, "(", str(mostPrioritaryJob.priority if mostPrioritaryJob else None), ") vs.", lessPrioritaryCPU, "(", str(lessPrioritaryCPU.priority() if lessPrioritaryCPU else None), ")"
		while mostPrioritaryJob and lessPrioritaryCPU and mostPrioritaryJob.priority > lessPrioritaryCPU.priority():
			if verbose: print "\tpremption!"
			preemptiveJob = heappop(self.activeJobsHeap)[1]
			preemptedCPU = heappop(self.activeCPUsHeap)
			preemptedJob = preemptedCPU.job

			# assign preemptive job to the CPU and push CPU in the correct heap
			preemptedCPU.job = preemptiveJob
			if preemptiveJob.preempted:
				preemptiveJob.preempted = False
				preemptedCPU.preemptionTimeLeft = self.alpha
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

			mostPrioritaryJob = heappeek(self.activeJobsHeap)[1] if len(self.activeJobsHeap) > 0 else None
			lessPrioritaryCPU = heappeek(self.activeCPUsHeap)
			if verbose: print "\t", mostPrioritaryJob, "(", str(mostPrioritaryJob.priority if mostPrioritaryJob else None), ") vs.", lessPrioritaryCPU, "(", str(lessPrioritaryCPU.priority()), ")"

		# activate CPUs whose preemption is finished
		self.activateCPUs()
		# compute tasks in active CPU
		for cpu in self.activeCPUsHeap:
			if cpu.job:
				print "\t", cpu, "computes one unit"
				cpu.job.computation += 1
		# compute preemptions
		for cpu in self.preemptedCPUs:
			cpu.preemptionTimeLeft -= 1
		if verbose:
			for i, cpu in enumerate(self.CPUs):
				print "\t", i, cpu
				if cpu in self.preemptedCPUs:
					print "\t(preempt)", cpu.preemptionTimeLeft, "left"

	def run(self, verbose=False):
		while(self.t < self.stop):
			self.incrementTime(verbose=verbose)
			if len(self.deadlineMisses) > 0:
				miss = self.deadlineMisses[0]
				print "DEADLINE MISS at t=", (miss[0] - 1), "for job", miss[1]
				break
			self.drawer.drawInstant(self.t)
		self.drawer.drawArrivalsAndDeadlines()

