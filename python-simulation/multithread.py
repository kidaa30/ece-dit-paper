import multiprocessing
import array
import main
import time
import algorithms
import pylab	
import sys

class WorkThread(object):
	def __init__(self, cdfIndex, numSystems, numCdfValues):
		self.cdfIndex = cdfIndex
		self.numCdfValues = numCdfValues
		self.numSystems = numSystems
	
	def run(self,resQueue,globalCdfIndex,cdfArray,resLock,outLock):
		self.globalCdfIndex = globalCdfIndex
		self.resQueue = resQueue
		self.cdfArray = cdfArray
		self.outLock = outLock
		allDone = False
		while(not allDone):
			result = self.runSystems(self.numSystems, self.cdfArray[self.cdfIndex])
			resQueue.put((self.cdfIndex,result))
  			resLock.acquire()
			if(globalCdfIndex.value < self.numCdfValues):
				self.cdfIndex = self.globalCdfIndex.value
				self.globalCdfIndex.value += 1
			else:
				allDone = True
   			resLock.release()
			
	def runSystems(self,numberOfSystems, constrDeadlineFactor):
		systemArray = main.generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False)
		verbose = False
	
		# Upper Limit Arrays
		busyPeriods = []
		firstDITs = []
		hyperTs = []
		# Feasibility Arrays
		bpResults = []
		ditResults = []
		hyperTResults = []
	
		# Compare algorithms
	
# 		print "Thread", self.cdfIndex, "start busy period tests..."
		bpStart = time.clock()
		for tau in systemArray:
			busyPeriods.append(algorithms.findBusyPeriod(tau))
		bpMedium = time.clock()
		for i, tau in enumerate(systemArray):
			bpResults.append(algorithms.dbf_test(tau, busyPeriods[i]))
		bpStop = time.clock()
	
	
# 		print "Thread", self.cdfIndex, "starting DIT value computation..."
		ditStart = time.clock()
		for i, tau in enumerate(systemArray):
			#print i
			firstDITs.append(algorithms.findFirstDIT(tau))
		ditMedium = time.clock()
		for i, tau in enumerate(systemArray):
			ditResults.append(algorithms.dbf_test(tau, firstDITs[i]))
		ditStop = time.clock()
		hyperTStart = time.clock()
		for i, tau in enumerate(systemArray):
			hyperTs.append(tau.hyperPeriod())
		hyperTMedium = time.clock()
		for i, tau in enumerate(systemArray):
			hyperTResults.append(algorithms.dbf_test(tau, hyperTs[i]))
		hyperTStop = time.clock()
	
		for i in range(len(systemArray)):
			assert bpResults[i] == ditResults[i] == hyperTResults[i]
	
# 		self.outLock.acquire()
# 		print "Thread", self.cdfIndex, "== Test Results (on " + str(numberOfSystems) + " tasks system)"
# 		if (verbose and len(systemArray) <= 10):
# 			for i in range(len(systemArray)):
# 				print "=== System", i
# 				print "\tbusy period:", busyPeriods[i]
# 				print "\tfirst DIT:", firstDITs[i]
# 				print "\tPPCM:", hyperTs[i]
# 		print "\tAlgorithms performance (upper limit computation + dbf test)"
# 		print "\t\tTime with busy period:", bpMedium - bpStart, "+", bpStop - bpMedium, " = ", bpStop - bpStart, "s"
# 		print "\t\tTime with DIT:", ditMedium - ditStart, "+", ditStop - ditMedium, " = ", ditStop - ditStart, "s"
# 		print "\t\tTime with hyperT:", hyperTMedium - hyperTStart, "+", hyperTStop - hyperTMedium, " = ", hyperTStop - hyperTStart, "s"
# 		feasibleSystemCnt = reduce(lambda x, y: x + (y is True), bpResults)
# 		print "\tFeasible?", feasibleSystemCnt, ", or about", int(round((feasibleSystemCnt * 100.0)/len(systemArray))), "%"
# 		self.outLock.release()
	
		return bpStop - bpMedium, bpMedium - bpStart, ditStop - ditMedium, ditMedium - ditStart, hyperTStop - hyperTMedium, hyperTMedium - hyperTStart
	
def processRun(cdfIndex, numSystems, numCdfValues, resQueue, globalCdfIndex, cdfArray, resLock, outLock):
	work = WorkThread(cdfIndex, numSystems, numCdfValues)
	work.run(resQueue, globalCdfIndex, cdfArray, resLock, outLock)
		
class ThreadManager(object):
	def __init__(self,cdf,threadCountLimit,numSystems):
		self.resultsQueue = multiprocessing.Queue()
		self.stdoutLock = multiprocessing.Lock()
		self.numSystems = numSystems
		self.cdf = multiprocessing.Array('d', cdf)
		self.numCdfValues = len(self.cdf)
		self.threadCountLimit = min(threadCountLimit,self.numCdfValues)
		self.threadList = []
		self.bpValue = array.array('f',[0.0])*self.numCdfValues
		self.bpTest = array.array('f',[0.0])*self.numCdfValues
		self.bpAll = array.array('f',[0.0])*self.numCdfValues
		self.ditValue = array.array('f',[0.0])*self.numCdfValues
		self.ditTest = array.array('f',[0.0])*self.numCdfValues
		self.ditAll = array.array('f',[0.0])*self.numCdfValues
		self.hyperTValue = array.array('f',[0.0])*self.numCdfValues
		self.hyperTTest = array.array('f',[0.0])*self.numCdfValues
		self.hyperTAll = array.array('f',[0.0])*self.numCdfValues
		
	def runAllThreads(self):
		self.curCdfIndex = multiprocessing.Value('i',0)
		resLock = multiprocessing.Lock()
		outLock = multiprocessing.Lock()
		resLock.acquire()
		for i in range(self.threadCountLimit):
			t = multiprocessing.Process(target=processRun, 
										args=(	self.curCdfIndex.value,self.numSystems,	self.numCdfValues, 
												self.resultsQueue,self.curCdfIndex,self.cdf,resLock,outLock))
			self.threadList.append(t)
			t.start()
			self.curCdfIndex.value += 1
		resLock.release()
			
		for i in range(self.numCdfValues):
			cdfIndex,res = self.resultsQueue.get()
			print "Got results for cdf", self.cdf[cdfIndex], [round(r,3) for r in res]
			self.bpValue[cdfIndex] = res[1]
			self.bpTest[cdfIndex] = res[0]
			self.bpAll[cdfIndex] = res[0] + res[1]
			self.ditValue[cdfIndex] = res[3]
			self.ditTest[cdfIndex] = res[2]
			self.ditAll[cdfIndex] = res[2] + res[3]
			self.hyperTValue[cdfIndex] = res[5]
			self.hyperTTest[cdfIndex] = res[4]
			self.hyperTAll[cdfIndex] = res[4] + res[5]
			
		for t in self.threadList:
			t.join()
			
if __name__ == '__main__':	
	NUMBER_OF_SYSTEMS = 1000
	cdfRange = [f/10.0 for f in range(10, 51)]
	manager = ThreadManager(cdfRange,4,NUMBER_OF_SYSTEMS)
	manager.runAllThreads()

 	pylab.figure()
 	pylab.plot(cdfRange, manager.bpAll, "k-", label="BP ALL")
 	pylab.plot(cdfRange, manager.bpValue, "k--", label="BP VALUE")
 	pylab.plot(cdfRange, manager.ditAll, "b-", label="DIT ALL")
 	pylab.plot(cdfRange, manager.ditValue, "b--", label="DIT VALUE")
 	pylab.plot(cdfRange, manager.hyperTAll, "r-", label="HYPERT ALL")
 	pylab.plot(cdfRange, manager.hyperTValue, "r--", label="HYPERT VALUE")
 	pylab.ylabel("time (s)")
 	pylab.xlabel("e")
 	pylab.title("Computation time for some values of e (" + str(NUMBER_OF_SYSTEMS) + " systems)")
 	pylab.legend(loc=0)
 # 	pylab.axis([cdfRange[0], cdfRange[-1], -0.5, 6])
 	pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
 	pylab.show()

		