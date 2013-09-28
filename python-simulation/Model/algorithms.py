import itertools
import math

from Helper import myAlgebra
from Model import newChineseRemainder
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
