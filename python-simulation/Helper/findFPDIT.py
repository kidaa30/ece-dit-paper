import myAlgebra
# from Model import TaskGenerator

import math
import heapq
import array


def newChineseRemainder(a, n):
    '''
    a is a list of lists, each sublist containing all possible a_i for the same n
    n is a list of the n_i values
    '''
    H = myAlgebra.lcmArray(n)

#   calculate all terms of the sums
    sumChunks = []
    for i in range(len(n)):
        sumChunks.append(array.array('i', [0])*len(a[i]))
        Mi = H // n[i]
        invMi = myAlgebra.modinv(Mi, n[i])
        for cnt, aValue in enumerate(a[i]):
            sumChunks[i][cnt] = (aValue * Mi * invMi) % H

#   calculate the sums from the precomputed terms
    results = [0]
    for i in range(len(n)):
        newResults = array.array('i', [0])*(len(a[i])*len(results))
        index = 0
        for j in range(len(a[i])):
            for r in results:
                newResults[index] = (r + sumChunks[i][j]) % H
                index += 1
        results = newResults

    return [r % H for r in results]


#not used anymore
def removeBadChineseRemainderResults(results, a, n):
    badResults = []
    for r in results:
        for cnt, i in enumerate(n):
            if len([_f for _f in [r % i == aValue for aValue in a[cnt]] if _f]) == 0:
                badResults.append(r)
                break

    for badR in badResults:
        results.remove(badR)

    return results


def isGoodResult(res, a, n):
    for cnt, i in enumerate(n):
        foundGoodA = False
        for aValue in a[cnt]:
            if res % i == aValue:
                foundGoodA = True
                break
        if not foundGoodA:
            return False
    return True


def newCongruencePrimalPower(primalSystem, aList):
    # Source : http://math.stackexchange.com/questions/120070/chinese-remainder-theorem-with-non-pairwise-coprime-moduli

    # Return a value x such that
    # x = a1 (mod p1^b1)
    # x = a2 (mod p2^b2)
    # ...
    # x = ak (mod pk^bk)
    # Returns None if no such x exists

    # Check that the values of aList are coherent in the primalSystem
    # and replace them by their value modulo p^b
    ps = {}
    for p in primalSystem:
        ps[p] = {}
        for b in primalSystem[p]:
            ps[p][b] = None
            for cnt, indice in enumerate(primalSystem[p][b]):
                if cnt == 0:
                    prime = int(math.pow(p, b))
                    aSet = set()
                    aSet.update([a % prime for a in aList[indice]])
                else:
                    aSet.intersection_update([a % prime for a in aList[indice]])
                    if not aSet:  # no a values in common
                        return None  # Impossible system
                ps[p][b] = list(aSet)

    # Group system into subsystems of the same p and solve them separately
    subX = {}
    maxB = {}
    for p in list(ps.keys()):
        maxB[p] = max(ps[p].keys())
        maxA = ps[p][maxB[p]]
        subX[p] = maxA

        # Check that all values are consistent modulo p^b
        # For that we check that ai = aj mod p^(b_min(i,j)) for all pairs
        # if the equations are coherent, we can only keep the one of biggest b

    # 3) Now we have a system respecting the condition of the CRT:
    # x = subX1 mod p1^maxB1
    # ...
    # x = subXk mod pk^maxBk

    # Create lists to use as parameters of our CRT function
    subXList = []
    pbArray = array.array('i', [0])*len(list(ps.keys()))
    for cnt, p in enumerate(ps.keys()):
        subXList.append(subX[p])
        pbArray[cnt] = int(math.pow(p, maxB[p]))

    return newChineseRemainder(subXList, pbArray)

class TaskCongruenceSystem(object):
	def __init__(self,xList,pList):
		self.xList = xList
		self.pList = pList

def findFPDIT(tau):
    # Requires to solve several system of modular equations

    # Construction of the intervals
    intervals = {task: list(range(task.D, task.T)) for task in tau.tasks}
    for task in tau.tasks:
        # 0, corresponding to the last/first case is missing from each interval
        intervals[task].append(0)
        # add Oi for the asynchronous case
        # This should have no effect in the synchronous case
        for j in range(len(intervals[i])):
            intervals[task][j] += task.O
            intervals[task][j] %= task.T

    T = [task.T for task in tau.tasks]
    Omax = max([task.O for task in tau.tasks])
    congruenceDict = {}
    
    for task in tau.tasks:
    	pFactors = myAlgebra.primeFactors(Task.T)
    	primalPowers = [pow(t,pFactors.count(t)) for t in set(pFactors)]
    	congruenceDict[task] = TaskCongruenceSystem(intervals[task],primalPowers)
    	
    allResults = multiCRP(congruenceDict)

    if not allResults:
        return None

    idles = list(zip(allResults, [False for i in range(len(allResults))]))
    heapq.heapify(idles)
    idleTuple = heapq.heappop(idles)
    tIdle = idleTuple[0]

    while(not isGoodResult(tIdle, intervals, T)):
        if not idles:
            return None
        idleTuple = heapq.heappop(idles)
        tIdle = idleTuple[0]

    while(tIdle <= Omax):
        heapq.heappush(idles, (tIdle+tau.hyperPeriod(), True))
        idleTuple = heapq.heappop(idles)
        tIdle = idleTuple[0]
        alreadyTested = idleTuple[1]
        while(not alreadyTested and not isGoodResult(tIdle, intervals, T)):
            if not idles:
                return None
            idleTuple = heapq.heappop(idles)
            tIdle = idleTuple[0]
            alreadyTested = idleTuple[1]

    return tIdle
    
    
def multiCRP(congruenceDict):
    tgsList = congruenceDict.values()
    ppSet = set()
    for t in tgsList:
        ppSet.update(t.pList)
    H = myAlgebra.lcmArray(ppSet)

#   calculate all terms of the sums
    sumChunks = {}
    for t in tgsList:
        tgsSumList = array.array('i', [0])*len(t.xList)
        for cnt,x in enumerate(t.xList):
            tgsSum = 0
            for p in t.pList:
                Mi = H // p
                invMi = myAlgebra.modinv(Mi, p)
                tgsSum += (x * Mi * invMi) % H
            tgsSumList[cnt] = tgsSum
        sumChunks[t] = append(tgsSumList)       

#   calculate the sums from the precomputed terms
    results = [0]
    for t in tgsList:
        newResults = array.array('i', [0])*(len(t.xList)*len(results))
        index = 0
        for cnt,x in enumerate(t.xList):
            for r in results:
                newResults[index] = (r + sumChunks[t][cnt]) % H
                index += 1
        results = newResults

    return [r % H for r in results]
    
def toPrimalPowerSystem(nList):
	# Source : http://math.stackexchange.com/questions/120070/chinese-remainder-theorem-with-non-pairwise-coprime-moduli
	# Transform a system into another equivalent system of the form
	# x = a1 (mod p1^b1)
	# x = a2 (mod p2^b2)
	# ...
	# x = ak (mod pk^bk)
	# (where p values are prime)

	# Return a dictionary encoding equalities (x = a (mod p^b)) of an equivalent primal system as primalSystem[p][b] = (list of indices of a)
	# Later, the list of values of a must be checked to be consistent
	n = len(nList)
	primalSystem = {}

	# preprocess the primes below max(n)
	nMax = max(nList)
	primes = primesBelow(nMax)

	for i in range(n):
		nFactors = primeFactors(nList[i])
		for p in nFactors:
			if p not in primalSystem:
				primalSystem[p] = {}
			b = nFactors.count(p)
			if b not in primalSystem[p]:
				primalSystem[p][b] = []
			# Add the indices to the list of indices to check
			primalSystem[p][b].append(i)
	return primalSystem
    
    
if __name__ == '__main__':
    pass