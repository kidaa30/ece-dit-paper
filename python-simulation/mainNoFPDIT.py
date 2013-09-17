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
    NUMBER_OF_SYSTEMS = 10
    noFPDITpcts2 = []
    noFPDITpcts3 = []
    noFPDITpcts4 = []
    CDFvalues = []
    for constrDeadlineFactor in [1/(x * 0.1) for x in range(1, 11)]:
        print(("CDF", constrDeadlineFactor))
        systemArray2 = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor, 2)
        systemArray3 = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor, 3)
        systemArray4 = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor, 4)
        firstDITs2 = []
        firstDITs3 = []
        firstDITs4 = []
        for i, tau in enumerate(systemArray2):
            firstDITs2.append(algorithms.findFirstPeriodicDIT(tau))
        for i, tau in enumerate(systemArray3):
            firstDITs3.append(algorithms.findFirstPeriodicDIT(tau))
        for i, tau in enumerate(systemArray4):
            firstDITs4.append(algorithms.findFirstPeriodicDIT(tau))
        noFPDITpcts2.append((100.0*len([x for x in firstDITs2 if x is None]))/len(firstDITs2))
        noFPDITpcts3.append((100.0*len([x for x in firstDITs3 if x is None]))/len(firstDITs3))
        noFPDITpcts4.append((100.0*len([x for x in firstDITs4 if x is None]))/len(firstDITs4))
        print(("Percentage of system with no FPDIT:", noFPDITpcts2[-1], noFPDITpcts3[-1], noFPDITpcts4[-1], "%"))
        CDFvalues.append(constrDeadlineFactor)

    pylab.figure()
    pylab.plot([1.0/x for x in CDFvalues], noFPDITpcts4, "b-^", label="4 Tasks")
    pylab.plot([1.0/x for x in CDFvalues], noFPDITpcts3, "k-o", label="3 Tasks")
    pylab.plot([1.0/x for x in CDFvalues], noFPDITpcts2, "g-s", label="2 Tasks")
    pylab.ylabel("%")
    pylab.xlabel("CDF")
    pylab.title("Number of systems with no FPDIT")
    pylab.legend(loc=0)
    # pylab.axis()
    # pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
    pylab.show()
