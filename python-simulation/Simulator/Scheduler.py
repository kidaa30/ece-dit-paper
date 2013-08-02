class SchedulerFJP(object):
	def __init__(self, tau):
		self.system = tau

	def priority(self, job):
		pass

	def maxPriority(self, jobs):
		return max([self.priority(job) for job in jobs])

	def minPriority(self, jobs):
		return min([self.priority(job) for job in jobs])


class EDF(SchedulerFJP):
	def priority(self, job):
		return 1.0/job.deadline
