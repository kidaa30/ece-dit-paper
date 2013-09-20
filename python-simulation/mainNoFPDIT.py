import random
import time
import pylab

from Model import algorithms
from Model import cspace
from Model import Task
from Model import TaskGenerator


def generateSystemArray(numberOfSystems, constrDeadlineFactor, tasksCnt, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 0.75
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = tasksCnt
        # maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        maxHyperT = -1
        Tmin = 5
        Tmax = 20
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print(("Generated task system # ", i))
            for task in tasks:
                    print(("\t", task))
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray

if __name__ == '__main__':
    NUMBER_OF_SYSTEMS = 10000
    noFPDITpcts = {}
    CDFvalues = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    nValues = [2, 3, 4, 5, 7, 10]
    symbols = ['D', 'o', 's', '*', 'v', '^']
    for taskCnt in nValues:
        print("n", taskCnt)
        noFPDITpcts[taskCnt] = {}
        for constrDeadlineFactor in CDFvalues:
            print("cdf", constrDeadlineFactor)
            systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor, taskCnt)
            firstDitsCnt = 0
            for i, tau in enumerate(systemArray):
                if algorithms.findFirstDIT(tau) is None:
                    firstDitsCnt += 1
            noFPDITpcts[taskCnt][constrDeadlineFactor] = (100*firstDitsCnt)/NUMBER_OF_SYSTEMS

    pylab.figure()
    for i, taskCnt in enumerate(reversed(nValues)):
        noFPDITpctsPerCDF = []
        for cdf in CDFvalues:
            noFPDITpctsPerCDF.append(noFPDITpcts[taskCnt][cdf])
        pylab.plot(CDFvalues, noFPDITpctsPerCDF, "-" + str(symbols[i]), label=str(taskCnt) + " Tasks")
    pylab.ylabel("%")
    pylab.xlabel("CDF")
    pylab.title("Number of systems with no FPDIT (n=" + str(NUMBER_OF_SYSTEMS) + ")")
    pylab.legend(loc=0)
    # pylab.axis()
    # pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
    pylab.show()
