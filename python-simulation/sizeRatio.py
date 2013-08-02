from Model import TaskGenerator
from Model import Task
from Model import cspace

import pylab
import time

if __name__ == "__main__":
	UTIL_BINS = [f/10.0 for f in range(1,11)]
	CDF_BINS = [e/1.0 for e in range(1,5)]
	NUMBER_OF_SYSTEMS = 10
	results = []
	for cdf in CDF_BINS:
		resCdf = []
		for cnt,util in enumerate(UTIL_BINS):
			resUtil = 0
			trueAsyncCnt = 0
			tasksLists = [TaskGenerator.generateTasks(Utot=util, n=3, maxHyperT=554400, Tmin=3, Tmax=15, synchronous=False, constrDeadlineFactor=cdf)
						for i in range(NUMBER_OF_SYSTEMS)]
			systems = [Task.TaskSystem(tasks) for tasks in tasksLists]

			for tau in systems:
				tSync = tau.firstSynchronousInstant()
				if not tSync:
					asyncCSpace = cspace.Cspace(tau)
					asyncCSpaceSize = asyncCSpace.size(tau)
					if asyncCSpaceSize > 0:
						syncTau = tau.synchronousEquivalent()
						syncCSpaceSize = syncTau.cSpaceSize()
						resUtil += float(syncCSpaceSize)/asyncCSpaceSize
						trueAsyncCnt += 1
			if(trueAsyncCnt > 0):
				resCdf.append(float(resUtil)/trueAsyncCnt)
			else:
				resCdf.append(0)
		results.append(resCdf)

	pylab.figure()
	markers = ['s','*','o','D']
	for cnt,cdf in enumerate(CDF_BINS):
		pylab.plot(UTIL_BINS, results[cnt], label="CDF " + str(cdf), marker=markers[cnt], markersize=7.0, linewidth=1.5)
	pylab.xlabel("system utilization")
	pylab.ylabel("size ratio")
	pylab.title("synchronous/asynchronous C-space size (" + str(NUMBER_OF_SYSTEMS) + " systems)")
	pylab.legend(loc=0)
#  	pylab.axis([0, 1, 0, 1])
	pylab.savefig("./plots/sizeratio_" + str(NUMBER_OF_SYSTEMS) + "-" + str(time.time()).replace(".", "") + ".eps")
	pylab.spectral()
	pylab.show()
