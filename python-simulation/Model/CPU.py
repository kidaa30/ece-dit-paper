class CPU(object):
	def __init__(self):
		self.job = None
		self.preemptionTimeLeft = 0

	def isIdle(self):
		return self.job is None

	def priority(self):
		return self.job.priority

	def __lt__(self, other):
		return self.job < other.job
