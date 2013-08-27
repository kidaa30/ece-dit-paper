import Simulator

import itertools
import pdb


class SchedulerDP(object):
    def __init__(self, tau):
        self.simu = None
        pass

    def initInstant(self):
        # called at the start of each instant (when time is incremented)
        pass

    def priority(self, job, simu):
        pass


class ChooseKeepEDF(SchedulerDP):
    def __init__(self, tau, prioOffset=0):
        super(ChooseKeepEDF, self).__init__(tau)
        self.spotlight = SpotlightEDF(tau, prioOffset=prioOffset)
        self.prioOffset = prioOffset

    def idleCPUsCount(self, simu):
        return len(filter(lambda cpu: cpu.job is None, simu.CPUs))

    def earliestPreempArrival(self, job, simu):
        # return earliest time at which job will be preempted if it is chosen now
        t = simu.t
        jobP = 1.0/(self.prioOffset + job.deadline - job.alpha())
        # test against priority of next arrival of each task
        candidate = None
        for task in simu.system.tasks:
            if t < task.O:
                nextArrival = task.O
            else:
                nextArrival = (t - task.O) + (task.T - (t - task.O) % task.T) + task.O
            prio = 1.0/(self.prioOffset + nextArrival + task.D)
            if candidate is None or (prio >= jobP and nextArrival < candidate):
                candidate = nextArrival
        return candidate

    def finishTime(self, job, simu):
        finish = simu.t
        finish += job.task.C - job.computation
        if job.preempted:
            finish += job.alpha()
        return finish

    def priority(self, job, simu):
        busyJobs = simu.getCurrentJobs(getWaitingJobs=False)
        if job in busyJobs:
            return 1.0/(self.prioOffset + job.deadline - job.alpha())
        epa = self.earliestPreempArrival(job, simu)
        finishTime = self.finishTime(job, simu)
        if epa - simu.t < job.alpha():  # better to idle
            return -1 * float("inf")
        else:
            if finishTime <= epa:
                return 1.0/(self.prioOffset + job.deadline)
            else:
                return 1.0/(self.prioOffset + job.deadline + job.alpha())


class SpotlightEDF(SchedulerDP):
    def __init__(self, tau, prioOffset=0):
        """ Non-optimal algorithm taking preemption cost into account.
        prioOffset should be bigger than the maximal preemption cost value"""
        super(SpotlightEDF, self).__init__(tau)
        self.prioOffset = prioOffset

    def isJobExecuting(self, job, simu):
        for cpu in simu.CPUs:
            if cpu.job is job:
                return True
        return False

    def priority(self, job, simu):
        if self.isJobExecuting(job, simu):
            return 1.0/(self.prioOffset + job.deadline - job.alpha())
        else:
            return 1.0/(self.prioOffset + job.deadline)


class SchedulerFJP(SchedulerDP):
    def priority(self, job, simu):
        if job.priority is not None:
            return job.priority


class EDF(SchedulerFJP):
    def priority(self, job, simu):
        super(SchedulerFJP, self).priority(job, simu)
        return 1.0/job.deadline


class SchedulerFTP(SchedulerFJP):
    def __init__(self, tau):
        super(SchedulerFTP, self).__init__(tau)
        self.priorities = self.orderPriorities(tau.tasks)

    def orderPriorities(self, taskArray):
        # return priorities array in priority order (decreasing)
        pass

    def priority(self, job, simu):
        super(SchedulerFTP, self).priority(job, simu)
        for i, task in enumerate(reversed(self.priorities)):  # priorities is decreasing
            if job.task is task:
                return i + 1  # prio = 0 is for idle cpu
        raise ValueError("Task of job " + str(job) + "not recognized")


class FixedPriority(SchedulerFTP):
    """Schedule the jobs according to given task priorities"""

    def __init__(self, tau, prioArray):
        """prioArray : list of priorities in the same order as tau.tasks"""
        self.prioArray = prioArray
        super(FixedPriority, self).__init__(tau)

    def orderPriorities(self, taskArray):
        assert len(self.prioArray) == len(taskArray), str(len(taskArray)) + "\t" + str(len(self.prioArray))
        priorities = []
        for prio, task in sorted(zip(self.prioArray, taskArray)):
            priorities.append(task)
        return priorities


class ExhaustiveFixedPriority(FixedPriority):
    def __init__(self, tau, preempTime, m, abortAndRestart):
        self.tau = tau
        self.preempTime = preempTime
        self.m = m
        self.abortAndRestart = abortAndRestart
        self.foundFeasible = None
        feasiblePriorities = self.exhaustiveSearch()
        super(ExhaustiveFixedPriority, self).__init__(tau, feasiblePriorities)

    def exhaustiveSearch(self):
        taskArray = self.tau.tasks
        priorities = [i for i in range(0, len(taskArray))]
        self.foundFeasible = False
        for prio in itertools.permutations(priorities):
            simu = Simulator.Simulator(self.tau, None, self.preempTime, self.m, FixedPriority(self.tau, prio), self.abortAndRestart)
            simu.run(stopAtDeadlineMiss=True, verbose=False)
            if simu.success():
                self.foundFeasible = True
                return prio
        return priorities  # foundFeasible is still False


class RM(SchedulerFTP):
    def orderPriorities(self, taskArray):
        priorities = []
        for task in taskArray:
            for i in range(len(priorities)):
                if task.T < priorities[i].T:
                    priorities.insert(i, task)
            if task not in priorities:
                priorities.append(task)
        return priorities



