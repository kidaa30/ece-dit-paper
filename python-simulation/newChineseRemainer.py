import myAlgebra
import algorithms


def chineseRemainder(a, n):
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

# print chineseRemainder([[1, 2], [4], [3, 6]], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([1, 4, 3], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([1, 4, 6], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([2, 4, 3], [3, 5, 7])
# print myAlgebra.chineseRemainderTheorem([2, 4, 6], [3, 5, 7])
# assert chineseRemainder([[1], [4], [3]], [3, 5, 7])[0] == myAlgebra.chineseRemainderTheorem([1, 4, 3], [3, 5, 7])
# 
# ps = myAlgebra.toPrimalPowerSystem([3, 5, 7])
# print myAlgebra.congruencePrimalPower(ps, [1, 4, 3])

print chineseRemainder([[1,2],[1,5]],[3,9])

#TODO convert primalsystem to usable stuff

def findFirstPeriodicDIT2(tau):
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

	T = [task.T for task in tau.tasks]
	Omax = max([task.O for task in tau.tasks])

	# Pre-processing for our congruence algorithm
	primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
	currentMin = None
	numberOfCombinations = reduce(lambda x, y: x*len(y), intervals, 1)
	for i, combination in enumerate(itertools.product(*intervals)):
		# if i % 1000 == 0: print "combination ", i, "/", numberOfCombinations
		tIdle = myAlgebra.congruencePrimalPower(primalSystem_T, combination)

		if tIdle is not None and tIdle <= Omax:
			while tIdle <= Omax:
				tIdle += tau.hyperPeriod()
		if tIdle is not None:
			if currentMin is None or tIdle < currentMin:
				currentMin = tIdle
	return currentMin

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
					ps[p][b] = aList[indice] % int(math.pow(p, b))
				else:
					if ps[p][b] != aList[indice] % int(math.pow(p, b)):
						return None  # Impossible system

	# Group system into subsystems of the same p and solve them separately
	subX = {}
	maxB = {}
	for p in ps.keys():
		# Check that all values are consistent modulo p^b
		# For that we check that ai = aj mod p^(b_min(i,j)) for all pairs
 		for bi in ps[p]: #TODO : verify should we only check for the smallest bi
			for bj in filter(lambda x: x > bi, primalSystem[p]):
				ai = ps[p][bi]
				aj = ps[p][bj]
				# by construction we know that bi < bj
				if ai % int(math.pow(p, bi)) != aj % int(math.pow(p, bi)):
					return None
		# if the equations are coherent, we can only keep the one of biggest b
		maxB[p] = max(ps[p].keys())
		subX[p] = ps[p][maxB[p]]

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

	return chineseRemainderTheorem(subXList, pbList)
