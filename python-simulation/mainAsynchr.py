import random
import time

import algorithms
import cspace
import Task
import TaskGenerator

def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
	systemArray = []
	for i in range(numberOfSystems):
		Umin = 0.25
		Umax = 0.75
		Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
		n = random.randint(1, 4)
		maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
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

if __name__ == '__main__':
	NUMBER_OF_SYSTEMS = 10
	for constrDeadlineFactor in range(5, 10):
		print "CONSTR DEAD FACTOR", constrDeadlineFactor
		systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor)
		start = time.clock()
		for i, tau in enumerate(systemArray):
			firstDIT = algorithms.findFirstPeriodicDIT(tau)
			sizeWithDIT = len(cspace.Cspace(tau, upperLimit="def"))  # will use first DIT if it exists
			upL = max([task.O for task in tau.tasks]) + 2 * tau.hyperPeriod()
			sizeWithoutDIT = len(cspace.Cspace(tau, upperLimit=upL))

			print "\tLimit :", firstDIT, "/", upL
			print "\tsize with DIT", sizeWithDIT
			print "\tsize without DIT", sizeWithoutDIT
			print "\t"
		stop = time.clock()
