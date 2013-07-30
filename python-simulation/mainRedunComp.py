import Task
import TaskGenerator
import algorithms
import cspace

import random
import time

def testSystem(tau):
	print "TESTING SYSTEM"
	print tau

	Omax = max([task.O for task in tau.tasks])
	fpdit = algorithms.findFirstDIT(tau)
	H = tau.hyperPeriod()
	tau_cspace = cspace.Cspace(tau)

	print "firstDIT", fpdit
	print "H", H
	print "#cstr of cspace", len(tau_cspace)

	if len(tau_cspace) <= 2000:
		twoPassStart = time.clock()
		cspacePruned = cspace.removeRedundancy(tau_cspace)
		twoPassStop = time.clock()

		onePassStart = time.clock()
		cspacepruned_onePass = cspace.removeRedundancy(tau_cspace, firstPass=False)
		onePassStop = time.clock()

		print "#cstr of cspace in 2 passes ", len(cspacePruned), "(time", twoPassStop - twoPassStart, ")"
		print "#cstr of cspace in 1 pass ", len(cspacepruned_onePass), "(time", onePassStop - onePassStart, ")"
		print "comparison of sizes", cspace.CspaceSize(tau, cspacepruned_onePass), "|", cspace.CspaceSize(tau, cspacePruned)
		return len(tau_cspace), twoPassStop - twoPassStart, onePassStop - onePassStart
	else:
		return None


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
	systemArray = generateSystemArray(10, 1)

	for i, tau in enumerate(systemArray):
		print "TEST NUMBER", i
		cstrSize, twoPassTime, onePassTime
