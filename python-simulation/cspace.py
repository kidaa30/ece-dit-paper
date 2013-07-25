import algorithms
import Task
import TaskGenerator

import random
import subprocess  # in order to launch GLPSOL
import math
import os.path
import re


def Cspace(tau, upperLimit="def", lowerLimit = 0):
	# return a system of inequations of the form
	# cst_1 * C_1 + cst_2 * C_2 + ... + cst_n * C_n <= CST
	# encoded as a list
	# [cst_1, cst_2, ..., cst_n, CST]

	Omax = max([task.O for task in tau.tasks])
	isSynchronous = (Omax == 0)

	if upperLimit == "def":
		firstDIT = algorithms.findFirstDIT(tau)
		if isSynchronous:
			upperLimit = firstDIT
			lowerLimit = 0
		else:
			if firstDIT is not None:
				upperLimit = firstDIT + tau.hyperPeriod()
				lowerLimit = firstDIT
			else:
				upperLimit = Omax + 2 * tau.hyperPeriod()
				lowerLimit = Omax

	# for each arrival and each deadline, create an equation
	equations = []
	for a, d in tau.dbf_intervals(lowerLimit, upperLimit):
		equations.append([algorithms.completedJobCount(t, a, d) for t in tau.tasks] + [d - a])

	return equations


def removeRedundancy(cspace):
	# Idea:
	# start with an empty list of cstr,
	# add each cstr only if it is not redundant
	# THEN test every remaining cstr against the others

	# first pass - filter against previous cstr
	newCspace = []
	for i, cstr in enumerate(cspace):
		if not isRedundant(cstr, newCspace):
			print "\tNon-redundant at step ", i, ":", cstr
			newCspace.append(cstr)

	# second pass - filter against all cstr
	# Note that the number of cstr should be small
	i = 0
	while i < len(newCspace):
		cstr = newCspace.pop(i)
		if not isRedundant(cstr, newCspace):
			newCspace.insert(i, cstr)
			i += 1
		else:
			print "\t", cstr, "was redundant against", newCspace

	return newCspace


def isRedundant(cstr, cspace):
	# cspace descibes constraints A X <= B
	# cstr is another C X <= d
	# We want to know if cstr is redundant w.r.t. cspace
	# Linear problem (solved by GLPK)
	# max C X
	# s.t.
	# 	AX <= b
	# 	C X <= d + 1
	# If the optimal value of the LP is > d, the
	if len(cspace) == 0:
		return False
	toGLPSOLData(cspace, cstr, "redundant_temp.dat")
	p = subprocess.Popen(args=["glpsol", "-m", os.path.join("GLPK","redundant.mod"),"-d", "redundant_temp.dat"], stdout=subprocess.PIPE)
	(output, err) = p.communicate()
	reRes = re.search(r".*?Display\ statement\ at\ line\ 28.*?(?P<number>[0-9]+).*", output, re.DOTALL)
	resultMaximization = int(reRes.group('number'))
	return resultMaximization <= cstr[-1]


def toGLPSOLData(cspace, cstr, filename):
	assert len(cspace) >= 1
	assert len(cspace[0]) >= 1
	with open(filename, 'w') as f:
		constrK = len(cspace)
		taskN = len(cspace[0]) - 1  # -1 because the last value in cspace is tk
		f.write("param constrK := " + str(constrK) + ";\n")
		f.write("param taskN := " + str(taskN) + ";\n")

		f.write("param nJob: ")
		for i in range(taskN):
			f.write(str(i + 1) + " ")
		f.write(":=\n")
		for i, eq in enumerate(cspace):
			f.write(str(i + 1) + "\t")
			for nJob in eq[:-1]:
				f.write(str(nJob) + " ")
			if i == constrK - 1:
				f.write(";")
			f.write("\n")

		f.write("param tk := \n")
		for i, eq in enumerate(cspace):
			f.write(str(i + 1) + "\t")
			f.write(str(eq[-1]))
			if i < constrK - 1:
				f.write(",\n")
			else:
				f.write(";\n")

		f.write("param nJobNew := \n")
		for i, nJobNew in enumerate(cstr[:-1]):
			f.write(str(i + 1) + "\t" + str(nJobNew))
			if i < taskN - 1:
				f.write(",\n")
			else:
				f.write(";\n")

		f.write("param tkNew := ")
		f.write(str(cstr[-1]))
		f.write(";\n")


def testCVector(cspace, tau):
	cvector = [task.C for task in tau.tasks]
	for i, equation in enumerate(cspace):
		res = 0
		for j in range(len(cvector)):
			res += equation[j]*cvector[j]
		if res > equation[-1]:
			#print "testCVector: error at equation ", i, equation, "with vector", cvector, "res:", res
			return False
	return True


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
		Tmax = 15
		tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
		if (verbose and numberOfSystems <= 10):
			print "Generated task system # ", i
			for task in tasks:
					print "\t", task
		systemArray.append(Task.TaskSystem(tasks))
	return systemArray


if __name__ == '__main__':
	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(5, 1, 1, 3))
	tasks.append(Task.Task(0, 4, 4, 8))
	tau = Task.TaskSystem(tasks)
	tau_Cspace = Cspace(tau)
	assert testCVector(tau_Cspace, tau) is False

	# "TEST2"

	tasks = []
	tasks.append(Task.Task(0, 1, 73, 154))
	tasks.append(Task.Task(0, 1, 381, 825))
	tasks.append(Task.Task(0, 1, 381, 400))
	tau = Task.TaskSystem(tasks)
	tau_Cspace = Cspace(tau, algorithms.findFirstDIT(tau))
	assert testCVector(tau_Cspace, tau) is True
	tau_Cspace_noredun = removeRedundancy(tau_Cspace)
	assert len(tau_Cspace) > len(tau_Cspace_noredun) == 2, str(tau_Cspace_noredun)

	# RANDOM TEST
	NUMBER_OF_SYSTEMS = 1
	systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, 1)
	for tau in systemArray:
		print tau
		print "cspace..."
		cspace = Cspace(tau)
		print "found ", len(cspace), "equations"
		print "remove redun..."
		cspace_noredun = removeRedundancy(cspace)
		print len(cspace), "=>", len(cspace_noredun), "equations left"
		print ""
		assert testCVector(cspace_noredun, tau) == testCVector(cspace, tau) == algorithms.dbf_test(tau)
		print "redundancy (necessary) condition ok"

