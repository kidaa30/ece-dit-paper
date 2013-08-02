from heapq import heapify, heappop, heappush
from Helper.ComparableMixin import ComparableMixin
from Model import Task

import Image as img
import ImageDraw as draw
import random



def heappeek(heap):
	if len(heap) == 0:
		return None
	return heap[0]


class Simulator(object):  # Global FJP only
	def __init__(self, tau, preempTime, m, schedulerName):
		self.system = tau
		self.alpha = preempTime

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

		self.output = ["" for task in tau.tasks]

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
		# remove finished job from CPUs
		for cpu in self.activeCPUsHeap:
			if cpu.job and cpu.job.isFinished():
				cpu.job = None
		# compute preemptions
		for cpu in self.preemptedCPUs:
			cpu.preemptionTimeLeft -= 1
		if verbose:
			for i, cpu in enumerate(self.CPUs):
				print "\tCPU", i, ":", cpu.job
				if cpu in self.preemptedCPUs:
					print "\t(preempt)", cpu.preemptionTimeLeft

	def prepareImage(self, stop):
		instantWidth = 20
		widthMargin = 20
		taskHeight = 100
		heightMargin = 20
		width = stop*instantWidth + 2 * widthMargin
		height = len(self.system.tasks) * taskHeight + 2 * heightMargin
		outImg = img.new("RGB", (width, height), "white")

		outDraw = draw.Draw(outImg)
		outDraw.line([widthMargin, height - heightMargin, widthMargin + instantWidth * stop, height - heightMargin], fill="black", width=3)
		# grid
		# - horizontal lines for tasks
		for i, task in enumerate(self.system.tasks):
			outDraw.line([widthMargin, height - heightMargin - (i + 1) * taskHeight, widthMargin + instantWidth * stop, height - heightMargin - (i + 1) * taskHeight], fill=128)
		# - vertical liens for instants
		for i in range(stop):
			outDraw.line([widthMargin + i * instantWidth, heightMargin, widthMargin + i * instantWidth, height - heightMargin], fill=64)
		return outImg, outDraw

	def run(self, stop):

		# outImg, outDraw = self.prepareImage(stop)
		# outImg.show()

		# # 1 random color per cpu
		# colors = ["rgb(" + ",".join([random.randint(255) for i in range(3)]) + ")" for j in range(m)]

		while(self.t < stop):
			self.incrementTime(verbose=False)

			# write output
			for i, task in enumerate(self.system.tasks):
				foundTask = False
				for j, cpu in enumerate(self.CPUs):
					if cpu.job and cpu.job.task is task:
						foundTask = True
						if cpu in self.preemptedCPUs:
							self.output[i] += 'P'
						else:
							self.output[i] += str(j)
				if not foundTask:
					self.output[i] += " "
				assert len(self.output[i]) == self.t + 1

			if len(self.deadlineMisses) > 0:
				miss = self.deadlineMisses[0]
				print "DEADLINE MISS at", miss[0], "for job", miss[1]
				break
		with open("out", "w") as f:
			for o in self.output:
				f.write(o + "\n")
			# timeline
			for i in range(len(self.output[0])):
				if i % 10 == 0:
					f.write(".")
				else:
					f.write(" ")


class CPU(object, ComparableMixin):
	def __init__(self):
		self.job = None
		self.preemptionTimeLeft = 0

	def isIdle(self):
		return self.job is None

	def priority(self):
		return self.job.priority

	def __lt__(self, other):
		return self.job < other.job


class Job(object, ComparableMixin):
	def __init__(self, task, arrival):
		self.task = task
		self.arrival = arrival
		self.deadline = arrival + task.D
		self.computation = 0
		self.priority = None  # maintained by the simulator
		self.preempted = False

	def isFinished(self):
		assert 0 <= self.computation <= self.task.C
		return self.computation == self.task.C

	def __lt__(self, other):
		return other is not None and (self.priority, id(self.task)) < (other.priority, id(other.task))

	def __repr__(self):
		return "(" + ", ".join([str(self.task), str(self.arrival), str(self.deadline), str(self.computation)]) + ")"


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
