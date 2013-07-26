import math
import myAlgebra

import array
import heapq


class Task(object):
	def __init__(self, O, C, D, T):
		self.O = O
		self.C = C
		self.D = D
		self.T = T

	def __repr__(self):
		reprStr =  ""
		reprStr += "("
		reprStr += str(self.O)
		reprStr += ", "
		reprStr += str(self.C)
		reprStr += ", "
		reprStr += str(self.D)
		reprStr += ", "
		reprStr += str(self.T)
		reprStr += ")"
		return reprStr

	def utilization(self):
		return (1.0*self.C)/self.T


class TaskSystem(object):
	def __init__(self, tasks):
		self.tasks = tasks
		self.hyperperiod = None
		#self.hyperT = self.hyperPeriod()

	def hyperPeriod(self):
		if not self.hyperperiod:
			Tset = [task.T for task in self.tasks]
			self.hyperperiod = myAlgebra.lcmArray(Tset)
		return self.hyperperiod

	def hasConstrainedDeadline(self):
		ok = True
		for task in self.tasks:
			ok = ok and task.D <= task.T
		return ok

	def isSynchronous(self):
		return max([task.O for task in self.tasks]) == 0

	def systemUtilization(self):
		u = 0
		for task in self.tasks:
			u += task.utilization()
		return u

	def __repr__(self):
		tauString = "TASK SYSTEM"
		for task in self.tasks:
			tauString += "\n\t" + str(task)
		return tauString


	def dbf_intervals(self, lowerLimit, upperLimit):
		starts = {}  # will contain all tasks first arrival
		for task in self.tasks:
			starts[task] = int(task.O + task.T * max(0, math.ceil((lowerLimit - task.O) / float(task.T))))
		dSet = set()
		for task in self.tasks:
			deadlineInRange = list(range(starts[task] + task.D, upperLimit + 1, task.T))
			if len(deadlineInRange) == 0:  # then add one anyway
				deadlineInRange = [starts[task] + task.D]
			dSet.update(deadlineInRange)
		deadlines = sorted(array.array('i', dSet))
		arrivals = []
		if not self.isSynchronous():
			heapq.heapify(arrivals)
			for task in self.tasks:
				heapTuple = (starts[task], task)
				heapq.heappush(arrivals, heapTuple)
		else:
			arrivals.append((0, self.tasks[0]))

		lastArrival = None
		lastDeadlineIndex = 0
		while arrivals:
			arrival, task = heapq.heappop(arrivals)
			if arrival != lastArrival:
				lastArrival = arrival
				dTuples = [(cnt, d) for cnt, d in enumerate(deadlines[lastDeadlineIndex:]) if d > arrival]
				dIndexes, dValues = zip(*dTuples)
				lastDeadlineIndex += dIndexes[0]  # add number of skipped deadlines
				for deadline in dValues:
					yield arrival, deadline
			nextArrival = arrival + task.T
			if self.isSynchronous() and nextArrival + task.D <= upperLimit:
				heapTuple = (nextArrival, task)
				heapq.heappush(arrivals, heapTuple)


import unittest

class TestTask(unittest.TestCase):
	def setUp(self):
		self.tasks = []
		#                 	O, C, D, T
		self.tasks.append(Task(0, 1, 3, 6))
		self.tasks.append(Task(0, 1, 3, 3))
		self.tasks.append(Task(1, 1, 5, 4))

		self.tasks2 = []
		#                 0, C, D, T
		self.tasks2.append(Task(0, 38, 73, 154))
		self.tasks2.append(Task(0, 156, 362, 825))
		self.tasks2.append(Task(0, 120, 362, 400))

		self.tau = TaskSystem(self.tasks)
		self.tau2 = TaskSystem(self.tasks[0:2])
		self.tau3 = TaskSystem(self.tasks2)


	def test_isSynchronous(self):
		self.assertFalse(self.tau.isSynchronous())
		self.assertTrue(self.tau2.isSynchronous())
		self.assertTrue(self.tau3.isSynchronous())


	def test_hasConstrainedDeadline(self):
		self.assertFalse(self.tau.hasConstrainedDeadline())
		self.assertTrue(self.tau2.hasConstrainedDeadline())
		self.assertTrue(self.tau3.hasConstrainedDeadline())


	def test_systemUtilization(self):
		self.assertEqual(0.5, self.tau2.systemUtilization())


	def test_hyperperiod(self):
		self.assertEqual(6, self.tau2.hyperPeriod())


if __name__ == '__main__':
	unittest.main()
# 	tasks = []
# 	#                 0, C, D, T
# 	tasks.append(Task(0, 1, 3, 6))
# 	tasks.append(Task(0, 1, 3, 3))
# 	tasks.append(Task(1, 1, 5, 4))
# 	tau = TaskSystem(tasks)
# 	assert not tau.isSynchronous(), "Unit Test FAIL : isSynchronous (1)"
# 	assert not tau.hasConstrainedDeadline(), "Unit Test FAIL : hasConstrainedDeadline (1)"
# 	tasks.pop()
# 	tau = TaskSystem(tasks)
# 	assert tau.isSynchronous(), "Unit Test FAIL : isSynchronous (2)"
# 	assert tau.hasConstrainedDeadline(), "Unit Test FAIL : hasConstrainedDeadline (2)"
# 	assert tau.systemUtilization() == 1.0/3 + 1.0/6
# 	assert tau.hyperPeriod() == 6
#
# 	tasks = []
# 	#                 0, C, D, T
# 	tasks.append(Task(0, 38, 73, 154))
# 	tasks.append(Task(0, 156, 362, 825))
# 	tasks.append(Task(0, 120, 362, 400))
# 	tau = TaskSystem(tasks)
# 	assert tau.isSynchronous(), "Unit Test FAIL : isSynchronous (3)"
# 	assert tau.hasConstrainedDeadline(), "Unit Test FAIL : hasConstrainedDeadline (3)"
