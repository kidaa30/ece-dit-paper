import Simulator

import itertools


class SchedulerDP(object):
	def __init__(self, tau):
		self.simu = None
		pass

	def priority(self, job, simu):
		pass


class ChooseKeepEDF(SchedulerDP):
	def __init__(self, tau):
		self.spotlight = SpotlightEDF(tau)
		self.idlePriority = None

	def idleCPUsCount(self, simu):
		return len(filter(lambda cpu: cpu.job is None, simu.CPUs))

	def earliestPreempArrival(self, job, simu):
		raise NotImplementedError, "This is wrinkling my brain"

	def finishTime(self, job, simu):
		finish = simu.t
		finish += job.task.C - job.computation
		if job.preempted:
			finish += simu.alpha
		return finish

	def priority(self, job, simu):
		if self.idleCPUsCount(simu) > 0:
			epa = {}  # earliest preemptive arrival
			finishTime = {}
			# compute epa and finishTime
			waitingJobs = simu.allCurentJobs(busyJobs=False)
			if job not in waitingJobs:
				# busy job (while there are idle CPU), maximal priority
				return float('inf')
			for job in waitingJobs:
				epa[job] = self.earliestPreempArrival(job)
				finishTime[job] = self.finishTime(job)
			# if there are easy jobs (jobs which can be computed entirely without being
			# preempted), there is surely no need to have idle times
			easyJobs = filter(lambda job: finishtime[job] <= epa[job], waitingJobs)
			if len(easyJobs) > 0:
				self.idlePriority = None
				if job in easyJobs:
					return 1.0/(job.deadline - simu.t)
				else:
					return 1.0/(job.deadline - simu.t + simu.alpha)  # I'm not sure this works
			else:
				self.idlePriority = 0
				return epa[job] - simu.alpha
		else:
			return self.spotlight.priority(job, simu)


class SpotlightEDF(SchedulerDP):
	def isJobExecuting(self, job, simu):
		for cpu in simu.CPUs:
			if cpu.job is job:
				return True
		return False

	def priority(self, job, simu):
		if self.isJobExecuting(job, simu):
			return 1.0/(job.deadline - simu.alpha)
		else:
			return 1.0/job.deadline


class SchedulerFJP(SchedulerDP):
	def __init__(self, tau):
		pass

	def priority(self, job, simu):
		if job.priority is not None:
			return job.priority


class EDF(SchedulerFJP):
	def priority(self, job, simu):
		super(SchedulerFJP, self).priority(job, simu)
		return 1.0/job.deadline


class SchedulerFTP(SchedulerFJP):
	def __init__(self, tau):
		self.priorities = self.orderPriorities(tau.tasks)

	def orderPriorities(self, taskArray):
		# return priorities array in priority order (decreasing)
		pass

	def priority(self, job, simu):
		super(SchedulerFJP, self).priority(job, simu)
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
		feasiblePriorities = self.exaustiveSearch()
		super(ExhaustiveFixedPriority, self).__init__(tau, feasiblePriorities)

	def exaustiveSearch(self):
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



