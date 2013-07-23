import myAlgebra
import algorithms
import math
import Task
import TaskGenerator

def newChineseRemainder(a, n):
	'''
	a is a list of lists, each sublist containing all possible a_i for the same n
	n is a list of the n_i values
	'''
	H = myAlgebra.lcmArray(n)

# 	calculate all terms of the sums
	sumChunks = []
	for i in range(len(n)):
		sumChunks.append([])
		Mi = H / n[i]
# 		if(myAlgebra.egcd_couple(Mi,n[i]) == 1):
		invMi = myAlgebra.modinv(Mi, n[i])
		for aValue in a[i]:
			sumChunks[i].append(aValue * Mi * invMi)

# 	calculate the sums from the precomputed terms
	results = [0]
	for i in range(len(n)):
		newResults = []
		for j in range(len(a[i])):
			for r in results:
				newResults.append(r + sumChunks[i][j])
		results = newResults

	return [r % H for r in results]

def removeBadChineseRemainderResults(results,a,n):
	badResults = []
	for r in results:
		for cnt,i in enumerate(n):
			if len(filter(None,[r % i == aValue for aValue in a[cnt]])) == 0:
				badResults.append(r)
				break
			
	for badR in badResults:
		results.remove(badR)
		
	return results

# print chineseRemainder([[1, 2], [4], [3, 6]], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([1, 4, 3], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([1, 4, 6], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([2, 4, 3], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([2, 4, 6], [3, 5, 7])
# assert chineseRemainder([[1], [4], [3]], [3, 5, 7])[0] == myAlgebra.chineseRemainderTheorem([1, 4, 3], [3, 5, 7])
# 
# ps = myAlgebra.toPrimalPowerSystem([3, 5, 7])
# print myAlgebra.congruencePrimalPower(ps, [1, 4, 3])

#TODO convert primalsystem to usable stuff

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
					if not aSet: #no a values in common
						return None  # Impossible system
				ps[p][b] = list(aSet)

	# Group system into subsystems of the same p and solve them separately
	subX = {}
	maxB = {}
	for p in ps.keys():
		maxB[p] = max(ps[p].keys())
		maxA = ps[p][maxB[p]]
		aSet = set(maxA)
		
		# Check that all values are consistent modulo p^b
		# For that we check that ai = aj mod p^(b_min(i,j)) for all pairs
		for bi in filter(lambda x: x < maxB[p], primalSystem[p]):
			iPow = int(math.pow(p, bi))
			ai = ps[p][bi]
			isSame = [len(filter(None, [y % iPow == a % iPow for y in ai])) > 0 for a in maxA]
 			aSet = set([a for a,ok in zip(aSet,isSame) if ok])
 			if not aSet:
 				return None
 		subX[p] = maxA
 		
# 				
			
		# Check that all values are consistent modulo p^b
		# For that we check that ai = aj mod p^(b_min(i,j)) for all pairs
#  		for bi in ps[p]: #TODO : verify should we only check for the smallest bi
# 			iPow = int(math.pow(p, bi))
# 			ai = ps[p][bi]
# 			for bj in filter(lambda x: x > bi, primalSystem[p]):
# 				aj = ps[p][bj]
# 				# by construction we know that bi < bj
# 				isSame = reduce(lambda x,y: x % iPow == y % iPow, ai,aj)
# 				aSet = set([a for a,ok in zip(aSet,isSame) if ok])
# 				
# 				aSet.intersection_update(jSet)
# 				if not aSet:
# 					return None
		# if the equations are coherent, we can only keep the one of biggest b

	# 3) Now we have a system respecting the condition of the CRT:
	# x = subX1 mod p1^maxB1
	# ...
	# x = subXk mod pk^maxBk

	# Create lists to use as parameters of our CRT function
	subXList = []
	pbList = []
	for p in ps.keys():
		subXList.append(subX[p])
		pbList.append(int(math.pow(p, maxB[p])))

	return newChineseRemainder(subXList, pbList)

#TODO : return None if no DIT
def newFindFirstPeriodicDIT(tau):
	# Requires to solve several system of modular equations

	# Construction of the intervals
  	intervals = [list(range(task.D, task.T)) for task in tau.tasks]
  	for i, task in enumerate(tau.tasks):
  		# 0, corresponding to the last/first case is missing from each interval
  		intervals[i].append(0)
  		# add Oi for the asynchronous case
  		# This should have no effect in the synchronous case
  		for j in range(len(intervals[i])):
  			intervals[i][j] += task.O
  			intervals[i][j] %= task.T
  			
  	print intervals

	T = [task.T for task in tau.tasks]
	Omax = max([task.O for task in tau.tasks])

	# Pre-processing for our congruence algorithm
	primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
	currentMin = None
# 	numberOfCombinations = reduce(lambda x, y: x*len(y), intervals, 1)
# 	for i, combination in enumerate(itertools.product(*intervals)):
		# if i % 1000 == 0: print "combination ", i, "/", numberOfCombinations
	print T
 	allResults = newCongruencePrimalPower(primalSystem_T, intervals)
 	print allResults
 	goodResults = removeBadChineseRemainderResults(allResults,intervals,T)
 	print goodResults
 	tIdle = min(goodResults)

	if tIdle is not None and tIdle <= Omax:
		while tIdle <= Omax:
			tIdle += tau.hyperPeriod()
	if tIdle is not None:
		if currentMin is None or tIdle < currentMin:
			currentMin = tIdle
	return currentMin

# 
# ps = toPrimalPowerSystem([6,9])
# subXList, pbList = newCongruencePrimalPower(ps,[[1, 2], [7,5,3]])
# results = chineseRemainder(subXList, pbList)
# print results
# print removeBadChineseRemainderResults(results,[[1, 2], [7,5,3]],[6,9])

system = Task.TaskSystem(TaskGenerator.generateTasks(1, 3, 554400, 2, 7, False))
print system
print newFindFirstPeriodicDIT(system)

def benchmarkNewChineseRemainder():
	pass