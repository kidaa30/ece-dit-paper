import Simulator

import itertools


class SchedulerFJP(object):
	def __init__(self, tau):
		pass

	def priority(self, job):
		pass

	def maxPriority(self, jobs):
		return max([self.priority(job) for job in jobs])

	def minPriority(self, jobs):
		return min([self.priority(job) for job in jobs])


class SchedulerFTP(SchedulerFJP):
	def __init__(self, tau):
		self.priorities = self.orderPriorities(tau.tasks)

	def orderPriorities(self, taskArray):
		# put the self.priorities array in priority order (decreasing)
		pass

	def priority(self, job):
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
	def __init__(self, tau, preemptTime, m, abortAndRestart):
		self.tau = tau
		self.preemptTime = preemptTime
		self.m = m
		self.abortAndRestart = abortAndRestart
		self.foundFeasible = None
		feasiblePriorities = self.exaustiveSearch()
		super(ExhaustiveFixedPriority, self).__init__(tau, feasiblePriorities)

	def exaustiveSearch(self):
		taskArray = self.tau.tasks
		priorities = [i for i in range(0, len(taskArray))]
		self.foundFeasible = False
		for prio in itertools.permutations(priorities):
			simu = Simulator.Simulator(self.tau, None, self.preemptTime, self.m, FixedPriority(self.tau, prio), self.abortAndRestart)
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


class EDF(SchedulerFJP):
	def priority(self, job):
		return 1.0/job.deadline
