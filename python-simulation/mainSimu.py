from Model import Task
from Model import TaskGenerator
from Model import algorithms
from Simulator import Simulator

import random

def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
	systemArray = []
	for i in range(numberOfSystems):
		Umin = 0.75
		Umax = 0.95
		Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
		n = 5
		maxHyperT = 180  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
		# maxHyperT = -1
		Tmin = 5
		Tmax = 50
		tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
		if (verbose and numberOfSystems <= 10):
			print "Generated task system # ", i
			for task in tasks:
					print "\t", task
		systemArray.append(Task.TaskSystem(tasks))
	return systemArray


# tasks = []
# # exemple from Patrick Meumeu's thesis pp. 128 (Fig. 4.13)
# tasks.append(Task.Task(0, 3, 7, 15))
# tasks.append(Task.Task(5, 2, 6, 6))
# tasks.append(Task.Task(3, 4, 10, 10))
# tau = Task.TaskSystem(tasks)

# # exemple from Wong/Burns paper (Improved Priority Assignment for the Abort-and-Restart (AR) Model)
# tasks.append(Task.Task(0, 4, 15, 15))
# tasks.append(Task.Task(3, 3, 11, 11))
# tau = Task.TaskSystem(tasks)

tau = generateSystemArray(1, 1)[0]

Omax = max([task.O for task in tau.tasks])
H = tau.hyperPeriod()
fpdit = algorithms.findFirstDIT(tau)

print tau

print "Omax", Omax
print "H", H
print "fpdit", fpdit

stop = Omax + 2 * H
if fpdit:
	stop = fpdit + H

print "stop", stop

simu = Simulator.Simulator(tau, stop=stop, preempTime=1, m=3, schedulerName="EDF", abortAndRestart=False)

try:
	simu.run(verbose=True)
except AssertionError:
	print "Something went wrong ! Close the image preview to see the callback"
	simu.drawer.outImg.show()
	raise

simu.drawer.outImg.show()
