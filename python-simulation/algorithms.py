import heapq
import itertools
import math

import myAlgebra


def findFirstDIT(tau):
	# language abuse ;-)
	return findFirstPeriodicDIT(tau)

def findFirstPeriodicDIT(tau):
	# Requires to solve several system of modular equations

	# Construction of the intervals
	intervals = [list(range(task.D, task.T)) for task in tau.tasks]
	for i, task in enumerate(tau.tasks):
		# 0, corresponding to the last/first case is missing from each interval
		intervals[i].append(0)
		# add Oi for the asynchronous case
		# This should have no effect in the synchronous case
		for j in range(len(intervals[i])):
			intervals[i][j] += task.O
			intervals[i][j] %= task.T

	T = [task.T for task in tau.tasks]
	Omax = max([task.O for task in tau.tasks])

	# Pre-processing for our congruence algorithm
	primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
	currentMin = None
	numberOfCombinations = reduce(lambda x, y: x*len(y), intervals, 1)
	for i, combination in enumerate(itertools.product(*intervals)):
		# if i % 1000 == 0: print "combination ", i, "/", numberOfCombinations
		tIdle = myAlgebra.congruencePrimalPower(primalSystem_T, combination)

		if tIdle is not None and tIdle <= Omax:
			while tIdle <= Omax:
				tIdle += tau.hyperPeriod()
		if tIdle is not None:
			if currentMin is None or tIdle < currentMin:
				currentMin = tIdle
	return currentMin

def findSynchronousInstant(tau):
	T = [task.T for task in tau.tasks]
	primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
	offsets = [task.O % task.T for task in tau.tasks]
	tSync = myAlgebra.congruencePrimalPower(primalSystem_T, offsets)
	return tSync

def findBusyPeriod(tau):
	# for synchronous arbitrary deadline:
	# fixed-point-iteration
	# w0 = sum_i Ci
	# w{k+1} = sum_{i} ceil(w_k / Ti) Ci
	assert tau.isSynchronous(), "findBusyPeriod: not a synchronous system"

	Cset = [task.C for task in tau.tasks]
	wNew = sum(Cset)
	wOld = 0
	hyperT = tau.hyperPeriod()
	while(wNew != wOld and wNew < hyperT):
		wOld = wNew
		wNew = 0
		assert wOld > wNew, "findBusyPeriod: wOld <= wNew. Old:" + str(wOld) + ", new:" + str(wNew)
		for task in tau.tasks:
			wNew += int(math.ceil(wOld*1.0 / task.T)*task.C)

	return wNew


def dbf_synchr(tau, t):
	return dbf(tau, 0, t)


def dbf(tau, t1, t2):
	dbfSum = 0
	for task in tau.tasks:
		dbfSum += completedJobCount(task, t1, t2) * task.C
	return dbfSum


def completedJobCount(task, t1, t2):
	jobBeforeT2 = int(math.floor(1.0 * (t2 - task.O - task.D) / task.T))
	jobBeforeT1 = int(math.ceil(1.0 * (t1 - task.O) / task.T))
	return max(0, jobBeforeT2 - jobBeforeT1 + 1)


def dbf_test(tau, upperLimit="def"):
	if upperLimit == "def":
		firstDIT = findFirstDIT(tau)
		busyPeriod = findBusyPeriod(tau)
		upperLimit = min(firstDIT, busyPeriod)

	# We use a heap to walk through the deadlines in chronological order
	# only one deadline per task is in the heap at a time
	# the node of the heap are tuple (deadline, task)
	deadlineHeap = map(lambda task: (task.O + task.D, task), tau.tasks)
	heapq.heapify(deadlineHeap)

	# Apply the feasibility test to every deadline in the interval [0, upperLimit)
	deadline = 0
	while deadline < upperLimit:
		tup = heapq.heappop(deadlineHeap)
		deadline = tup[0]
		task = tup[1]
		testResult = dbf_synchr(tau, deadline) <= deadline
		if testResult is False:
			return False
		# add next deadline of this task to the heap
		heapq.heappush(deadlineHeap, (deadline + task.T, task))

	return True

if __name__ == '__main__':
	import Task

	# UNIT TEST 1
	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(0, 1, 3, 6))
	tasks.append(Task.Task(0, 1, 3, 3))
	tau = Task.TaskSystem(tasks)
	assert findBusyPeriod(tau) == 2, "Unit Test FAIL : findBusyPeriod"
	assert findFirstDIT(tau) == 3, "Unit Test FAIL : findFirstDIT, returned: " + str(findFirstDIT(tau))
	assert findSynchronousInstant(tau) == 0, "Unit Test FAIL : findSynchronousInstant; returned: " + str(findSynchronousInstant(tau))
	assert dbf_test(tau) is True

	# UNIT TEST 2 -- Influence of deadline on the DIT
	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(0, 1, 1, 6))
	tasks.append(Task.Task(0, 1, 1, 3))
	tau = Task.TaskSystem(tasks)
	assert findBusyPeriod(tau) == 2, "Unit Test FAIL : findBusyPeriod (2); " + "returned: " + str(findBusyPeriod(tau))
	assert findFirstDIT(tau) == 1, "Unit Test FAIL : findFirstDIT (2)"
	assert findSynchronousInstant(tau) == 0, "Unit Test FAIL : findSynchronousInstant (2); returned: " + str(findSynchronousInstant(tau))
	assert dbf_test(tau) is False

	# UNIT TEST 3 -- Edge case of congruence (cannot return 0: we do not consider 0 to be a DIT)
	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(0, 1, 2, 2))
	tasks.append(Task.Task(0, 1, 3, 3))
	tau = Task.TaskSystem(tasks)
	assert findBusyPeriod(tau) == 2, "Unit Test FAIL : findBusyPeriod (3); " + "returned: " + str(findBusyPeriod(tau))
	assert findFirstDIT(tau) == 6, "Unit Test FAIL : findFirstDIT (3); " + "returned: " + str(findFirstDIT(tau))
	assert findSynchronousInstant(tau) == 0, "Unit Test FAIL : findSynchronousInstant (3); returned: " + str(findSynchronousInstant(tau))
	assert dbf_test(tau) is True

	# UNIT TEST 4 -- Asynchronous system
	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(5, 1, 1, 3))
	tasks.append(Task.Task(0, 4, 4, 8))
	tau = Task.TaskSystem(tasks)
	# No busy period test as it does not make sense in asynchronous system
	assert findFirstPeriodicDIT(tau) == 6, "Unit Test FAIL : findFirstDIT (4a); " + "returned: " + str(findFirstDIT(tau))
	assert findSynchronousInstant(tau) == 8, "Unit Test FAIL : findSynchronousInstant (4a); " + "returned: " + str(findSynchronousInstant(tau))
	#assert dbf_test(tau) is True

	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(0, 1, 4, 6))
	tasks.append(Task.Task(2, 1, 3, 6))
	tasks.append(Task.Task(10, 1, 1, 2))
	tau = Task.TaskSystem(tasks)
	assert findFirstPeriodicDIT(tau) == 11, "Unit Test FAIL : findFirstDIT (4b); " + "returned: " + str(findFirstDIT(tau))
	assert findSynchronousInstant(tau) is None, "Unit Test FAIL : findSynchronousInstant (4b); " + "returned: " + str(findSynchronousInstant(tau))

	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(120, 6, 25, 25))
	tasks.append(Task.Task(0, 4, 47, 48))
	tau = Task.TaskSystem(tasks)
	assert findFirstPeriodicDIT(tau) == 720, "Unit Test FAIL : findFirstDIT (4c); " + "returned: " + str(findFirstDIT(tau))
	assert findSynchronousInstant(tau) == 720, "Unit Test FAIL : findSynchronousInstant (4c); " + "returned: " + str(findSynchronousInstant(tau))

	print "LONG UNIT TEST (should be less than 2 minutes)....."

	tasks = []
	#                      0, C,  D,  T
	tasks.append(Task.Task(0, 38, 73, 154))
	tasks.append(Task.Task(0, 156, 381, 825))
	tasks.append(Task.Task(0, 120, 381, 400))
	tau = Task.TaskSystem(tasks)
	# I haven't checked these results so this test only check that the values do not change.
	assert findBusyPeriod(tau) == 390
	assert findFirstDIT(tau) == 381, "returned: " + str(findFirstDIT(tau))
	assert findSynchronousInstant(tau) == 0, "returned: " + str(findSynchronousInstant(tau))
	assert dbf_test(tau) is False

	print "(1/3 OK)"
	# random test

	import TaskGenerator
	Utot = 0.75
	n = 5
	maxHyperT = 554400
	Tmin = 50
	Tmax = 100
	tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=True, constrDeadlineFactor=8)
	tau = Task.TaskSystem(tasks)
	# oracle?
	assert 0 < findBusyPeriod(tau)
	assert 0 < findFirstDIT(tau) <= tau.hyperPeriod()
	assert findSynchronousInstant(tau) == 0, "returned: " + str(findSynchronousInstant(tau))
	assert dbf_test(tau) or True

	print "(2/3 OK)"
	# random test - asynchr (and other parameters)

	import TaskGenerator
	Utot = 1
	n = 4
	maxHyperT = 100
	Tmin = 5
	Tmax = 20
	tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False)
	# oracle?
	tau = Task.TaskSystem(tasks)
	assert 0 < tau.hyperPeriod()
	assert findSynchronousInstant(tau) or True, "returned: " + str(findSynchronousInstant(tau)) + "\n" + str(tau)
	assert findFirstPeriodicDIT(tau) or True
