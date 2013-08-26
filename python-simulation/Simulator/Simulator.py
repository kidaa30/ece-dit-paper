from heapq import heapify, heappop, heappush
import pdb

from Model.CPU import CPU
from Model import algorithms
from Model.Job import Job
import Drawer


def heappeek(heap):
	return heap[0] if len(heap) > 0 else None


class Simulator(object):  # Global FJP only
	def __init__(self, tau, stop, preempTime, m, scheduler, abortAndRestart):
		"""stop can be set to None for default value"""
		self.system = tau
		self.m = m
		self.alpha = preempTime
		self.AR = abortAndRestart
		if stop is None:
			fpdit = algorithms.findFirstDIT(tau)
			if fpdit:
				stop = fpdit + tau.hyperPeriod()
			else:
				stop = tau.omax() + tau.hyperPeriod()
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

		self.scheduler = scheduler

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

	def allCurrentJobs(self, busyJobs=True):
		allTuples = self.activeJobsHeap
		if busyJobs:
			busyTuples = filter(lambda tupl: tupl[1] is not None, [(None, cpu.job) for cpu in self.CPUs])
			allTuples = allTuples + busyTuples
		return [b for (a, b) in allTuples]

	def updateHeaps(self):
		# possible bottleneck : job heap is reconstructed (2 times) at each t
		newJobHeap = []
		for prio, job in self.activeJobsHeap:
			newJobHeap.append((-1 * job.priority, job))
		self.activeJobsHeap = newJobHeap
		heapify(self.activeCPUsHeap)
		heapify(self.activeJobsHeap)

	def mostPrioritaryJob(self):
		return heappeek(self.activeJobsHeap)[1] if len(self.activeJobsHeap) > 0 else None

	def lessPrioritaryCPU(self):
		return heappeek(self.activeCPUsHeap)

	def incrementTime(self, verbose=True):
		self.t += 1
		if verbose: print "t=", self.t
		# remove finished job from CPUs
		for cpu in self.activeCPUsHeap:
			if cpu.job and cpu.job.isFinished():
				cpu.job = None
		self.updateHeaps()
		# check for deadline miss
		for job in self.allCurrentJobs():
			assert job
			if self.t >= job.deadline:
				assert job.computation < job.task.C
				self.deadlineMisses.append((self.t, job))
		# check for job arrival
		for task in self.system.tasks:
			if self.t >= task.O and self.t % task.T == task.O % task.T:
				newJob = Job(task, self.t)
				if verbose: print "\tarrival of job:", newJob
				newJob.priority = self.scheduler.priority(newJob, self)
				print "prio of ", newJob, "is", newJob.priority
				heappush(self.activeJobsHeap, (-1 * newJob.priority, newJob))

		# preemptions
		# TODO : deal with idle times scheduling
		while True:
			# update priorities (DP)
			for job in self.allCurrentJobs():
				job.priority = self.scheduler.priority(job, self)
				if verbose:
					print "prio of ", job, "is now", job.priority
			self.updateHeaps()
			# check for preemptions
			if verbose:
				print "\t", self.mostPrioritaryJob(), "(", str(self.mostPrioritaryJob().priority if self.mostPrioritaryJob() else None), ") vs.", self.lessPrioritaryCPU(), "(", str(self.lessPrioritaryCPU().priority() if self.lessPrioritaryCPU() else None), ")"
			if self.mostPrioritaryJob() and self.lessPrioritaryCPU() and self.mostPrioritaryJob().priority > self.lessPrioritaryCPU().priority():
				if verbose:
					print "\tpremption!"
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
				if verbose: print "\t", mostPrioritaryJob, "(", str(mostPrioritaryJob.priority if mostPrioritaryJob else None), ") vs.", lessPrioritaryCPU, "(", str(lessPrioritaryCPU.priority() if lessPrioritaryCPU else None), ")"
			else:
				break
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
				print "\t", i, cpu
				if cpu in self.preemptedCPUs:
					print "\t(preempt)", cpu.preemptionTimeLeft, "left"

	def run(self, stopAtDeadlineMiss=True, verbose=False):
		while(self.t < self.stop):
			self.incrementTime(verbose=verbose)

			for miss in self.deadlineMisses:
				if verbose: print "DEADLINE MISS at t=", (miss[0] - 1), "for job", miss[1]
			if len(self.deadlineMisses) > 0:
				if stopAtDeadlineMiss:
					break
			else:
				self.deadlineMisses = []
				self.drawer.drawInstant(self.t)
		self.drawer.drawArrivalsAndDeadlines()

	def success(self):
		assert self.t >= 0, "Simulator.success: call run() first"
		return self.t == self.stop
