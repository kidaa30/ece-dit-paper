from Model import TaskGenerator
from Model import Task
from Model import cspace

import pylab
import time
import concurrent.futures
import itertools

def parallelFunc(util, cdf):
	tasks = TaskGenerator.generateTasks(Utot=util, n=3, maxHyperT=554400, Tmin=5, Tmax=20, synchronous=False, constrDeadlineFactor=cdf)
	tau = Task.TaskSystem(tasks)
	res = None
	
	tSync = tau.firstSynchronousInstant()
	if not tSync:
		asyncCSpace = cspace.Cspace(tau)
		asyncCSpaceSize = asyncCSpace.size(tau)
		if asyncCSpaceSize > 0:
			syncTau = tau.synchronousEquivalent()
			syncCSpaceSize = syncTau.cSpaceSize()
			res = float(syncCSpaceSize)/asyncCSpaceSize
	return res

if __name__ == "__main__":
	UTIL_BINS = [f/10.0 for f in range(1,11)]
	CDF_BINS = [e/5.0 for e in range(1,6)]
	nSystems = 10
	
	
	executor = concurrent.futures.ProcessPoolExecutor()
	parallelArgs = list(itertools.product(CDF_BINS,UTIL_BINS,range(nSystems)))
	print(parallelArgs)
	unzippedArgs = list(zip(*parallelArgs))
	argResults = {a:r for (a,r) in zip(parallelArgs, executor.map(parallelFunc,unzippedArgs[0],unzippedArgs[1]))}
	
# 	print(argResults)
	results = []
	for cdf in CDF_BINS:
		resCdf = []
		for util in UTIL_BINS:
			resUtil = 0
			trueAsyncCnt = 0
			for n in range(nSystems):
				res = argResults[(cdf,util,n)]
				if res is not None:
					resUtil += res
					trueAsyncCnt += 1
			if trueAsyncCnt > 0:
				resCdf.append(resUtil/float(trueAsyncCnt))
			else:
				resCdf.append(0)
		results.append(resCdf)

	pylab.figure()
	markers = ['s','*','o','D','^']
	for cnt,cdf in enumerate(CDF_BINS):
		pylab.plot(UTIL_BINS, results[cnt], label="CDF " + str(cdf), marker=markers[cnt], markersize=7.0, linewidth=1.5)
	pylab.xlabel("system utilization")
	pylab.ylabel("size ratio")
	pylab.title("synchronous/asynchronous C-space size (" + str(nSystems) + " systems)")
	pylab.legend(loc=0)
#  	pylab.axis([0, 1, 0, 1])
	pylab.savefig("./plots/sizeratio_" + str(nSystems) + "-" + str(time.time()).replace(".", "") + ".png")
	pylab.spectral()
	pylab.show()
