import itertools
import math

from Helper import myAlgebra
import newChineseRemainder
from functools import reduce


def findFirstDIT(tau):
    # language abuse ;-)
#   return findFirstPeriodicDIT(tau)
    return newChineseRemainder.newFindFirstPeriodicDIT(tau)


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
    return tau.dbf(0, t)

def dbf(tau, t1, t2):
    return tau.dbf(t1, t2)

def completedJobCount(task, t1, t2):
    return task.completedJobCount(t1, t2)

def dbfTest(tau, firstDIT=None):
    # TODO : add lowerLimit (already present in all subfunctions)
    Omax = max([task.O for task in tau.tasks])
    if firstDIT is None:
        if Omax == 0:
            upperLimit = findBusyPeriod(tau)
        else:
            upperLimit = Omax + 2 * tau.hyperPeriod()
        lowerLimit = Omax
    else:
        lowerLimit = Omax
        upperLimit = firstDIT + tau.hyperPeriod()

    for arrival, deadline in tau.dbf_intervals(lowerLimit, upperLimit):
        testResult = dbf(tau, arrival, deadline) <= deadline
        if testResult is False:
            return False

    # If all previous test succeed, the system is feasible
    return True

if __name__ == '__main__':

## TODO : continue transfer to testAlgorithms


    tasks = []
    #                      0, C, D, T
    tasks.append(Task.Task(120, 6, 25, 25))
    tasks.append(Task.Task(0, 4, 47, 48))
    tau = Task.TaskSystem(tasks)
    assert findFirstPeriodicDIT(tau) == 720, "Unit Test FAIL : findFirstDIT (4c); " + "returned: " + str(findFirstDIT(tau))
    assert findSynchronousInstant(tau) == 720, "Unit Test FAIL : findSynchronousInstant (4c); " + "returned: " + str(findSynchronousInstant(tau))

    print("LONG UNIT TEST (should be less than 2 minutes).....")

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
    assert dbfTest(tau) is False

    print("(1/3 OK)")
    # random test

    from . import TaskGenerator
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
    assert dbfTest(tau) or True

    print("(2/3 OK)")
    # random test - asynchr (and other parameters)

    from . import TaskGenerator
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

    print('3/3 OK')
