import algorithms
import Task


def Cspace(tau, upperLimit="def"):
	# return a system of equation of the form
	# cst_1 * C_1 + cst_2 * C_2 + ... + cst_n * C_n <= CST
	# encoded as a list
	# [cst_1, cst_2, ..., cst_n, CST]

	Omax = max([task.O for task in tau.tasks])
	isSynchronous = (Omax == 0)

	if upperLimit == "def":
		firstDIT = algorithms.findFirstDIT(tau)
		if isSynchronous:
			upperLimit = firstDIT
		else:
			if firstDIT is not None:
				upperLimit = firstDIT + tau.hyperPeriod()
			else:
				upperLimit = Omax + 2 * tau.hyperPeriod()

	# for each arrival and each deadline, create an equation
	# TODO: more intelligent stuff
	equations = []
	for task in tau.tasks:
		for a in [0] if isSynchronous else range(task.O, upperLimit + 1, task.T):
			for task2 in tau.tasks:
				for d in filter(lambda x: x > a, range(task2.O + task2.D, upperLimit + 1, task2.T)):
					equations.append([algorithms.completedJobCount(t, a, d) for t in tau.tasks] + [d - a])

	return equations


def toGLPSOLData(cspace, filename):
	# suppose the last cstr of cspace is the one to be checked
	with open(filename, 'w') as f:
		assert len(cspace) > 1
		assert len(cspace[0]) >= 1
		constrK = len(cspace) - 1  # - 1 because the last one is to be checked
		taskN = len(cspace[0]) - 1  # -1 because the last value in cspace is tk
		f.write("param constrK := " + str(constrK) + ";\n")
		f.write("param taskN := " + str(taskN) + ";\n")

		f.write("param nJob: ")
		for i in range(taskN):
			f.write(str(i + 1) + " ")
		f.write(":=\n")
		for i, eq in enumerate(cspace[:-1]):  # the last cstr is to be tested
			f.write(str(i + 1) + "\t")
			for nJob in eq[:-1]:
				f.write(str(nJob) + " ")
			if i == constrK - 1:
				f.write(";")
			f.write("\n")

		f.write("param tk := \n")
		for i, eq in enumerate(cspace[:-1]):
			f.write(str(i + 1) + "\t")
			f.write(str(eq[-1]))
			if i < constrK - 1:
				f.write(",\n")
			else:
				f.write(";\n")

		f.write("param nJobNew := \n")
		for i, nJobNew in enumerate(cspace[-1][:-1]):
			f.write (str(i + 1) + "\t" + str(nJobNew))
			if i < taskN - 1:
				f.write(",\n")
			else:
				f.write(";\n")

		f.write("param tkNew := ")
		f.write(str(cspace[-1][-1]))
		f.write(";\n")


def testCVector(cspace, cvector):
	for i, equation in enumerate(cspace):
		res = 0
		for j in range(len(cvector)):
			res += equation[j]*cvector[j]
		if res > equation[-1]:
			print "testCVector: error at equation ", i, equation, "with vector", cvector, "res:", res
			return False
	return True

if __name__ == '__main__':
	tasks = []
	#                      0, C, D, T
	tasks.append(Task.Task(5, 1, 1, 3))
	tasks.append(Task.Task(0, 4, 4, 8))
	tau = Task.TaskSystem(tasks)

	tau_Cspace = Cspace(tau)
	print "found ", len(tau_Cspace), "equations"

	assert testCVector(tau_Cspace, [task.C for task in tau.tasks]) is False

	print "TEST2"

	tasks = []
	tasks.append(Task.Task(0, 1, 73, 154))
	tasks.append(Task.Task(0, 1, 381, 825))
	tasks.append(Task.Task(0, 1, 381, 400))
	tau = Task.TaskSystem(tasks)
	print "computing Cspace..."
	tau_Cspace = Cspace(tau, 381)  # 381 = DIT of the system (obviously ;D)
	print "found ", len(tau_Cspace), "equations"

	assert testCVector(tau_Cspace, [task.C for task in tau.tasks]) is True

	toGLPSOLData(tau_Cspace, "redundant_test.dat")
