import random
import time
import pylab

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
		n = 3
		# maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
		maxHyperT = -1
		Tmin = 5
		Tmax = 20
		tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
		if (verbose and numberOfSystems <= 10):
			print "Generated task system # ", i
			for task in tasks:
					print "\t", task
		systemArray.append(Task.TaskSystem(tasks))
	return systemArray

if __name__ == '__main__':
	NUMBER_OF_SYSTEMS = 10000
	noFPDITpcts = []
	CDFvalues = []
	for constrDeadlineFactor in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]:
		#print "CONSTR DEAD FACTOR", constrDeadlineFactor
		systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor)
		firstDITs = []
		upLs = []
		for i, tau in enumerate(systemArray):
			start = time.clock()

			firstDITs.append(algorithms.findFirstPeriodicDIT(tau))
			if firstDITs[-1] is not None:
				firstDITs[-1] += tau.hyperPeriod()
			upLs.append(max([task.O for task in tau.tasks]) + 2 * tau.hyperPeriod())
			# print "\t", i, "Limit :", firstDITs[-1] if firstDITs[-1] is None else firstDITs[-1], "/", upLs[-1]

			# sizeWithDIT = len(cspace.Cspace(tau, upperLimit="def"))  # will use first DIT if it exists
			# if firstDIT is None:
			# 	sizeWithoutDIT = sizeWithDIT
			# else:
			# 	sizeWithoutDIT = len(cspace.Cspace(tau, upperLimit=upL))
			# print "\tsize with DIT\t", sizeWithDIT
			# print "\tsize no DIT\t", sizeWithoutDIT
			# stop = time.clock()
			# print "\ttime: ", stop - start, "s"
			# print "\t"
		print "CDF", constrDeadlineFactor
		noFPDITpcts.append((100.0*len(filter(lambda x: x is None, firstDITs)))/len(firstDITs))
		print "Percentage of system with no FPDIT:", noFPDITpcts[-1], "%"
		CDFvalues.append(constrDeadlineFactor)

	pylab.figure()
	pylab.plot(CDFvalues, noFPDITpcts, "r-o", label="No FPDIT %")
	pylab.ylabel("%")
	pylab.xlabel("CDF")
	pylab.title("Number of systems with no FPDIT")
	pylab.legend(loc=0)
	# pylab.axis()
	# pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
	pylab.show()
