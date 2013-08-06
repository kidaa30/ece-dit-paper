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
		for i, task in enumerate(reversed(self.priorities)):  # priorities is decrasing
			if job.task is task:
				return i
		raise ValueError("Task of job " + str(job) + "not recognized")


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
