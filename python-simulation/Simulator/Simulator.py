from heapq import heapify, heappop, heappush
from Helper import ComparableMixin
from Model.Task import Task
from Model.CPU import CPU
from Scheduler import EDF
from Model.Job import Job
import Drawer


def heappeek(heap):
	if len(heap) == 0:
		return None
	return heap[0]


class Simulator(object):  # Global FJP only
	def __init__(self, tau, stop, preempTime, m, schedulerName):
		self.system = tau
		self.m = m
		self.alpha = preempTime
		self.stop = stop

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
		# check for deadline miss
		for job in self.activeJobsHeap + filter(None, [cpu.job for cpu in self.CPUs]):
			if self.t > job.deadline:
				self.deadlineMisses.append((self.t, job))
		# check for job arrival
		for task in self.system.tasks:
			if self.t % task.T == task.O:
				newJob = Job(task, self.t)
				if verbose: print "\tarrival of job:", newJob
				newJob.priority = self.scheduler.priority(newJob)
				heappush(self.activeJobsHeap, newJob)
		# preemptions
		mostPrioritaryJob = heappeek(self.activeJobsHeap)
		lessPrioritaryCPU = heappeek(self.activeCPUsHeap)
		existIdleCPUs = len(filter(lambda cpu: cpu.isIdle(), self.CPUs)) > 0
		while mostPrioritaryJob and lessPrioritaryCPU and (existIdleCPUs or mostPrioritaryJob.priority > lessPrioritaryCPU.priority()):
			if verbose: print "\tjob", mostPrioritaryJob, "preempted", lessPrioritaryCPU.job
			preemptiveJob = heappop(self.activeJobsHeap)
			preemptedCPU = heappop(self.activeCPUsHeap)
			preemptedJob = preemptedCPU.job

			# assign preemptive job to the CPU and push CPU in the correct heap
			preemptedCPU.job = preemptiveJob
			if preemptiveJob.preempted:
				preemptiveJob.preempted = False
				preemptedCPU.preemptionTimeLeft = self.alpha
				# For AR Model : use preemptedJob.computation
				self.preemptedCPUs.add(preemptedCPU)
			else:
				heappush(self.activeCPUsHeap, preemptedCPU)

			# put the preempted job back in the active job heap
			if (preemptedJob):
				preemptedJob.preempted = True
				heappush(self.activeJobsHeap, preemptedJob)

			mostPrioritaryJob = heappeek(self.activeJobsHeap)
			lessPrioritaryCPU = heappeek(self.activeCPUsHeap)
			existIdleCPUs = len(filter(lambda cpu: cpu.isIdle(), self.CPUs)) > 0

		# activate CPUs whose preemption is finished
		self.activateCPUs()
		# compute tasks in active CPU
		for cpu in self.activeCPUsHeap:
			if cpu.job:
				cpu.job.computation += 1
		# compute preemptions
		for cpu in self.preemptedCPUs:
			cpu.preemptionTimeLeft -= 1
		if verbose:
			for i, cpu in enumerate(self.CPUs):
				print "\tCPU", i, ":", cpu.job
				if cpu in self.preemptedCPUs:
					print "\t(preempt)", cpu.preemptionTimeLeft

	def run(self):

		# outImg, outDraw = self.prepareImage(stop)
		# outImg.show()

		while(self.t < self.stop):
			self.incrementTime(verbose=True)

			self.drawer.drawInstant(self.t)

			if len(self.deadlineMisses) > 0:
				miss = self.deadlineMisses[0]
				print "DEADLINE MISS at", miss[0], "for job", miss[1]
				break
		# with open("out", "w") as f:
		# 	for o in self.output:
		# 		f.write(o + "\n")
		# 	# timeline
		# 	for i in range(len(self.output[0])):
		# 		if i % 10 == 0:
		# 			f.write(".")
		# 		else:
		# 			f.write(" ")

