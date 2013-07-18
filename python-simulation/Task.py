import math
import myAlgebra

class Task(object):
	def __init__(self, O, C, D, T):
		self.O = O
		self.C = C
		self.D = D
		self.T = T

	def __repr__(self):
		reprStr =  ""
		reprStr += "("
		reprStr += str(self.O)
		reprStr += ", "
		reprStr += str(self.C)
		reprStr += ", "
		reprStr += str(self.D)
		reprStr += ", "
		reprStr += str(self.T)
		reprStr += ")"
		return reprStr

	def utilization(self):
		return (1.0*self.C)/self.T


class TaskSystem(object):
	def __init__(self, tasks):
		self.tasks = tasks
		#self.hyperT = self.hyperPeriod()

	def hyperPeriod(self):
		Tset = [task.T for task in self.tasks]
		return myAlgebra.lcmArray(Tset)

	def hasConstrainedDeadline(self):
		ok = True
		for task in self.tasks:
			ok = ok and task.D <= task.T
		return ok

	def isSynchronous(self):
		return sum([task.O for task in self.tasks]) == 0

	def systemUtilization(self):
		u = 0
		for task in self.tasks:
			u += task.utilization()
		return u

	def __repr__(self):
		tauString = "TASK SYSTEM"
		for task in self.tasks:
			tauString += "\n\t" + str(task)
		return tauString



if __name__ == '__main__':
	tasks = []
	#                 0, C, D, T
	tasks.append(Task(0, 1, 3, 6))
	tasks.append(Task(0, 1, 3, 3))
	tasks.append(Task(1, 1, 5, 4))
	tau = TaskSystem(tasks)
	assert not tau.isSynchronous(), "Unit Test FAIL : isSynchronous (1)"
	assert not tau.hasConstrainedDeadline(), "Unit Test FAIL : hasConstrainedDeadline (1)"
	tasks.pop()
	tau = TaskSystem(tasks)
	assert tau.isSynchronous(), "Unit Test FAIL : isSynchronous (2)"
	assert tau.hasConstrainedDeadline(), "Unit Test FAIL : hasConstrainedDeadline (2)"
	assert tau.systemUtilization() == 1.0/3 + 1.0/6
	assert tau.hyperPeriod() == 6

	tasks = []
	#                 0, C, D, T
	tasks.append(Task(0, 38, 73, 154))
	tasks.append(Task(0, 156, 362, 825))
	tasks.append(Task(0, 120, 362, 400))
	tau = TaskSystem(tasks)
	assert tau.isSynchronous(), "Unit Test FAIL : isSynchronous (3)"
	assert tau.hasConstrainedDeadline(), "Unit Test FAIL : hasConstrainedDeadline (3)"
