import random
import time

import Task
import TaskGenerator
import algorithms

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
	NUMBER_OF_SYSTEMS = 1000
	for constrDeadlineFactor in range(1, 10):
		print "CONSTR DEAD FACTOR", constrDeadlineFactor
		systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor)
		successCount = 0
		start = time.clock()
		for i, tau in enumerate(systemArray):
			if constrDeadlineFactor == 1 and i % 100 == 0:
				print i, "/", NUMBER_OF_SYSTEMS, "..."
			successCount += 1 if algorithms.findFirstDIT(tau) else 0
		stop = time.clock()
		print "Found", successCount, "/", NUMBER_OF_SYSTEMS, "DITs in ", stop - start, "seconds."
