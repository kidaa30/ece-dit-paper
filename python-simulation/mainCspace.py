from helper import systems
from model import Task
from model import cspace as cs
from model import algorithms

import sys

tau = None

# tasks = []
# tasks.append(Task.Task(O, C, D, T))
# tasks.append(Task.Task(O, C, D, T))
# tau = Task.TaskSystem(tasks)

# tau = systems.Meumeu

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        tau = Task.TaskSystem.fromFile(f)

print(tau)
print("cspace...")
cspace = cs.Cspace(tau)
print("found ", len(cspace), "constraints")
print("remove redun...")
cspace_noredun = cspace.removeRedundancy()
print(len(cspace), "=>", len(cspace_noredun), "constraints left")
for cstr in cspace_noredun:
    print(cstr)
print("")
resultCSPACE = cs.testCVector(cspace_noredun, [task.C for task in tau.tasks])
resultCSPACENOREDUN = cs.testCVector(cspace, [task.C for task in tau.tasks])
resultDBF = algorithms.dbfTest(tau)
assert resultCSPACE == resultCSPACENOREDUN == resultDBF, str(resultCSPACE) + str(resultCSPACENOREDUN) + str(resultDBF)
print("synchronous instant", algorithms.findSynchronousInstant(tau))
print("The volume of the C-space is", cspace_noredun.size(tau))
