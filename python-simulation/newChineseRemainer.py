import myAlgebra
import algorithms

def chineseRemainder(a,n):
	'''
	a is a list of lists, each sublist containing all possible a_i for the same n
	n is a list of the n_i values
	'''
	sumChunks = []
	
	H = myAlgebra.lcmArray(n)
	
# 	calculate all terms of the sums
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

print chineseRemainder([[1,2],[4],[3,6]],[3,5,7])
print myAlgebra.chineseRemainderTheorem([1,4,3],[3,5,7])
print myAlgebra.chineseRemainderTheorem([1,4,6],[3,5,7])
print myAlgebra.chineseRemainderTheorem([2,4,3],[3,5,7])
print myAlgebra.chineseRemainderTheorem([2,4,6],[3,5,7])
assert chineseRemainder([[1],[4],[3]],[3,5,7])[0] == myAlgebra.chineseRemainderTheorem([1,4,3],[3,5,7])

ps = myAlgebra.toPrimalPowerSystem([3,5,7])
print myAlgebra.congruencePrimalPower(ps, [1,4,3])

#TODO convert primalsystem to usable stuff
