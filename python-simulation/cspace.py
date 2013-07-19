import algorithms
import Task


def Cspace(tau, upperLimit="def"):
	# return a system of equation of the form
	# cst_1 * C_1 + cst_2 * C_2 + ... + cst_n * C_n <= CST
	# encoded as a list
	# [cst_1, cst_2, ..., cst_n, CST]

	isSynchronous = max([task.O for task in tau.tasks]) == 0

	if upperLimit == "def":
		if isSynchronous:
			upperLimit = algorithms.findFirstDIT(tau)
		else:
			upperLimit = max([task.O for task in tau.tasks]) + 2 * tau.hyperPeriod()

	# for each arrival and each deadline, create an equation
	equations = []
	for task in tau.tasks:
		# print task
		for a in [0] if isSynchronous else range(task.O, upperLimit + 1, task.T):
			for task2 in tau.tasks:
				# print "\t", task2
				for d in filter(lambda x: x > a, range(task2.O + task2.D, upperLimit + 1, task2.T)):
					equations.append([algorithms.completedJobCount(t, a, d) for t in tau.tasks] + [d - a])

	return equations

def testCVector(cspace, cvector):
	for i, equation in enumerate(cspace):
		res = 0
		for j in range(len(cvector)):
			res += equation[j]*cvector[j]
		if res > equation[-1]:
			print "testCVector: error at equation ", i, equation, "with vector", cvector, "res:" , res
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
	tau_Cspace = Cspace(tau, 381)  # 381 = DIT of the system ;)
	print "found ", len(tau_Cspace), "equations"

	assert testCVector(tau_Cspace, [task.C for task in tau.tasks]) is True
