import random
from Model import Task
from Model import TaskGenerator

def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
	systemArray = []
	for i in range(numberOfSystems):
		Umin = 0.75
		Umax = 0.95
		Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
		n = 5
		maxHyperT = 180  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
		# maxHyperT = -1
		Tmin = 5
		Tmax = 50
		tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
		if (verbose and numberOfSystems <= 10):
			print "Generated task system # ", i
			for task in tasks:
					print "\t", task
		systemArray.append(Task.TaskSystem(tasks))
	return systemArray


# exemple from Patrick Meumeu's thesis pp. 128 (Fig. 4.13) (alpha???)
tasks = []
tasks.append(Task.Task(0, 3, 7, 15, alpha=1))
tasks.append(Task.Task(5, 2, 6, 6, alpha=1))
tasks.append(Task.Task(3, 4, 10, 10, alpha=1))
Meumeu = Task.TaskSystem(tasks)

# exemple from Wong/Burns paper (Improved Priority Assignment for the Abort-and-Restart (AR) Model)
tasks = []
tasks.append(Task.Task(0, 6, 60, 60))
tasks.append(Task.Task(0, 4, 32, 32))
tasks.append(Task.Task(0, 3, 25, 25))
tasks.append(Task.Task(0, 5, 50, 50))
tasks.append(Task.Task(0, 2, 100, 100))
WongBurns = Task.TaskSystem(tasks)

# exemple of non-optimality of EDF with preemptions
tasks = []
tasks.append(Task.Task(0, 3, 6, 6, alpha=2))
tasks.append(Task.Task(1, 2, 4, 4, alpha=2))
EDFNonOptimal = Task.TaskSystem(tasks)

# Anomaly: removing Task (0,1,2,4) renders the system unfeasible!
# This is also an example of necessary idle time and non-optimality of EDF/SpotlightEDF
tasks = []
tasks.append(Task.Task(0, 2, 4, 4, alpha=2))
#tasks.append(Task.Task(0, 1, 2, 4, alpha=2))
tasks.append(Task.Task(1, 1, 1, 4, alpha=2))
Anomaly1 = Task.TaskSystem(tasks)

# # Example of non-optimality of SpotlightEDF
tasks = []
tasks.append(Task.Task(0, 3, 6, 7, alpha=2))
tasks.append(Task.Task(0, 2, 7, 7, alpha=2))
tasks.append(Task.Task(2, 1, 1, 7, alpha=2))
SpotlightEDFNonOptimal = Task.TaskSystem(tasks)

# # PreemptNoIdle (preemptTime = 1)
tasks = []
tasks.append(Task.Task(0, 6, 9, 11, alpha=1))
tasks.append(Task.Task(0, 2, 11, 11, alpha=1))
tasks.append(Task.Task(3, 2, 2, 11, alpha=1))
PreemptNoIdle = Task.TaskSystem(tasks)

# # Must Idle (preemptTime = 2)
tasks = []
tasks.append(Task.Task(0, 3, 8, 8, alpha=2))
tasks.append(Task.Task(0, 3, 5, 8, alpha=2))
tasks.append(Task.Task(1, 1, 1, 8, alpha=2))
MustIdle = Task.TaskSystem(tasks)

# DPOnly (preemptTime = 1)
tasks = []
tasks.append(Task.Task(0, 4, 8, 8, alpha=1))
tasks.append(Task.Task(0, 1, 5, 8, alpha=1))
tasks.append(Task.Task(3, 1, 1, 8, alpha=1))
tasks.append(Task.Task(5, 1, 1, 8, alpha=1))
DPOnly = Task.TaskSystem(tasks)

# CKEDF non-optimal
tasks = []
tasks.append(Task.Task(0, 4, 9, 9, alpha=1))
tasks.append(Task.Task(0, 1, 5, 9, alpha=1))
tasks.append(Task.Task(3, 1, 1, 9, alpha=1))
tasks.append(Task.Task(5, 1, 1, 9, alpha=1))
CKEDFNonOptimal = Task.TaskSystem(tasks)

# Meat Grinder (unfeasible for preemptTime > 0 although U = ~0.5)
tasks = []
tasks.append(Task.Task(0, 2, 100, 100, alpha=1))
tasks.append(Task.Task(1, 1, 1, 2, alpha=1))
MeatGrinder = Task.TaskSystem(tasks)

# LongTransitive
tasks = []
tasks.append(Task.Task(0, 45, 150, 150, alpha=23))
tasks.append(Task.Task(20, 10, 50, 50, alpha=23))
tasks.append(Task.Task(20, 10, 50, 50, alpha=23))
LongTransitive = Task.TaskSystem(tasks)

