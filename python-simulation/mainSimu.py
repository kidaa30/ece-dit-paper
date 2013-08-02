from Model import Task
from Simulator import Simulator

tasks = []
# exemple from Patrick Meumeu's thesis pp. 128 (Fig. 4.13)
tasks.append(Task.Task(0, 3, 7, 15))
tasks.append(Task.Task(5, 2, 6, 6))
tasks.append(Task.Task(3, 4, 10, 10))
tau = Task.TaskSystem(tasks)
simu = Simulator.Simulator(tau, preempTime=2, m=1, schedulerName="EDF")
simu.run(70)
