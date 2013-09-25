from Model import Task
from Model import TaskGenerator
from Model import cspace as cs
from Model import algorithms
import random

def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 0.75
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = 3
        maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        # maxHyperT = -1
        Tmin = 5
        Tmax = 20
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print("Generated task system # ", i)
            for task in tasks:
                    print("\t", task)
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray

tasks = []
#                      0, C, D, T
tasks.append(Task.Task(0, 1, 5, 7))
tasks.append(Task.Task(0, 1, 7, 11))
tasks.append(Task.Task(0, 1, 10, 13))
tau = Task.TaskSystem(tasks)
print(tau)
tau_Cspace = cs.Cspace(tau)
tau_Cspace_noredun = tau_Cspace.removeRedundancy()

print("FINAL CSPACE")
for cstr in tau_Cspace_noredun:
    print(cstr)
print(len(tau_Cspace), "=>", len(tau_Cspace_noredun), "constraints left")

tasks = []
#                      0, C, D, T
tasks.append(Task.Task(5, 1, 1, 3))
tasks.append(Task.Task(0, 4, 4, 8))
tau = Task.TaskSystem(tasks)
tau_Cspace = cs.Cspace(tau)
assert cs.testCVector(tau_Cspace, [task.C for task in tau.tasks]) is False

# "TEST2"

tasks = []
tasks.append(Task.Task(0, 1, 73, 154))
tasks.append(Task.Task(0, 1, 381, 825))
tasks.append(Task.Task(0, 1, 381, 400))
tau = Task.TaskSystem(tasks)
tau_Cspace = cs.Cspace(tau, algorithms.findFirstDIT(tau))
assert cs.testCVector(tau_Cspace, [task.C for task in tau.tasks]) is True
tau_Cspace_noredun = tau_Cspace.removeRedundancy()
assert len(tau_Cspace) > len(tau_Cspace_noredun) == 2, str(tau_Cspace_noredun)

# RANDOM TEST
NUMBER_OF_SYSTEMS = 10
systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, 0.5)
for tau in systemArray:
    print(tau)
    print("cspace...")
    cspace = cs.Cspace(tau)
    print("found ", len(cspace), "constraints")
    print("remove redun...")
    cspace_noredun = cspace.removeRedundancy()
    print(len(cspace), "=>", len(cspace_noredun), "constraints left")
    print("")
    resultCSPACE = cs.testCVector(cspace_noredun, [task.C for task in tau.tasks])
    resultCSPACENOREDUN = cs.testCVector(cspace, [task.C for task in tau.tasks])
    resultDBF = algorithms.dbfTest(tau)
    assert resultCSPACE == resultCSPACENOREDUN == resultDBF, str(resultCSPACE) + str(resultCSPACENOREDUN) + str(resultDBF)
    print("redundancy (necessary) condition ok")
    print("synchronous instant", algorithms.findSynchronousInstant(tau))
    print("cspacesize", cspace_noredun.size(tau))
