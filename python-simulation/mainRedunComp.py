from Model import Task
from Model import TaskGenerator
from Model import algorithms
from Model import cspace

import pylab

import random
import time

def testSystem(tau, maxCstrcnt=1000):
	print "TESTING SYSTEM"
	print tau

	Omax = max([task.O for task in tau.tasks])
	fpdit = algorithms.findFirstDIT(tau)
	H = tau.hyperPeriod()
	tau_cspace = cspace.Cspace(tau)

	print "firstDIT", fpdit
	print "H", H
	print "#cstr of cspace", len(tau_cspace)

	if len(tau_cspace) <= maxCstrcnt:
		twoPassStart = time.clock()
		cspacePruned = tau_cspace.removeRedundancy()
		twoPassStop = time.clock()

		onePassStart = time.clock()
		cspacepruned_onePass = tau_cspace.removeRedundancy(firstPass=False)
		onePassStop = time.clock()

		print "#cstr of cspace in 2 passes ", len(cspacePruned), "(time", twoPassStop - twoPassStart, ")"
		print "#cstr of cspace in 1 pass ", len(cspacepruned_onePass), "(time", onePassStop - onePassStart, ")"
		print "comparison of sizes", cspacepruned_onePass.size(tau), "|", cspacePruned.size(tau)
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
	systemArray = generateSystemArray(100, 1)
	cstrSizes = []
	twoTimes = []
	oneTimes = []

	for i, tau in enumerate(systemArray):
		print "TEST NUMBER", i
		returnTuple = testSystem(tau, maxCstrcnt=1000)
		if returnTuple is not None:
			cstrSize, twoPassTime, onePassTime = returnTuple[0], returnTuple[1], returnTuple[2]
			cstrSizes.append(cstrSize)
			twoTimes.append(twoPassTime)
			oneTimes.append(onePassTime)

	pylab.figure()
	pylab.plot(cstrSize, twoTimes, "g-s", label="Two passes")
	pylab.plot(cstrSize, oneTimes, "b-r", label="One pass")
	pylab.ylabel("s")
	pylab.xlabel("cstr number")
	pylab.title("Comparison of redundancy removal techniques")
	pylab.legend(loc=0)
	# pylab.axis()
	# pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
	pylab.show()
