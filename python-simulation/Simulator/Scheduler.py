import Simulator

import itertools
import pdb


class SchedulerDP(object):
    def __init__(self, tau):
        pass

    def priority(self, job, simu):
        pass

    def preemptEqualPriorities(self):
        return True

    def initInstant(self):
        # called at the start of each instant (when time is incremented)
        pass

    # General purpose functions for schedulers

    def isJobExecuting(self, job, simu):
        return job in [cpu.job for cpu in simu.CPUs]

    def finishTime(self, job, simu):
        return simu.t + job.computationLeft() + (job.alpha() if job.preempted else 0)


class SpotlightEDF(SchedulerDP):
    def __init__(self, tau):
        """ Non-optimal algorithm taking preemption cost into account."""
        super(SpotlightEDF, self).__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks])

    def priority(self, job, simu):
        if self.isJobExecuting(job, simu):
            return 1.0/(self.prioOffset + job.deadline - job.alpha())
        else:
            return 1.0/(self.prioOffset + job.deadline)


class SchedulerFJP(SchedulerDP):
    def priority(self, job, simu):
        if job.priority is not None:
            return job.priority

    def preemptEqualPriorities(self):
        return False


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
    def __init__(self, tau, nbrCPUs, abortAndRestart):
        self.tau = tau
        self.m = nbrCPUs
        self.abortAndRestart = abortAndRestart
        self.foundFeasible = None
        feasiblePriorities = self.exhaustiveSearch()
        super(ExhaustiveFixedPriority, self).__init__(tau, feasiblePriorities)

    def exhaustiveSearch(self):
        taskArray = self.tau.tasks
        priorities = [i for i in range(0, len(taskArray))]
        self.foundFeasible = False
        for prio in itertools.permutations(priorities):
            simu = Simulator.Simulator(self.tau, None, self.m, FixedPriority(self.tau, prio), self.abortAndRestart)
            simu.run(stopAtDeadlineMiss=True)
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
