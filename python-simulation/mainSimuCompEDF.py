from Model import algorithms
from Simulator import Simulator
from Simulator import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler
import systems

NUMBER_OF_SYSTEMS = 1000

# schedulers = [Scheduler.EDF, ChooseKeepEDF.ChooseKeepEDF, PALLF.PALLF]
schedulers = [Scheduler.EDF, LBLScheduler.LBLEDF]

interest = []  # system with weird property

results = {}
scores = {}
for sched in schedulers:
    results[sched] = []
    scores[sched] = 0

for i in range(NUMBER_OF_SYSTEMS):
    print(i)
    tau = systems.generateSystemArray(1, 1)[0]
    if i == 0:
        tau = systems.CloudAtlas
    # tau = systems.test
    # print(tau)

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    fpdit = algorithms.findFirstDIT(tau)
    stop = Omax + 10 * H  # FIXME
    if fpdit:
        stop = fpdit + H

    for sched in schedulers:
        simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=sched(tau), abortAndRestart=False, drawing=False)
        simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)
        results[sched].append(simu.success())

    # quickhack
    rEDF = results[Scheduler.EDF][-1]
    rLBLEDF = results[LBLScheduler.LBLEDF][-1]
    if rEDF and not rLBLEDF:
        interest.append(tau)

# compute score
for i in range(NUMBER_OF_SYSTEMS):
    for sched in schedulers:
        if results[sched][i]:
            undefeated = True
            for otherSched in schedulers:
                if otherSched is not sched and results[otherSched][i]:
                    undefeated = False
                    break
            if undefeated:
                scores[sched] += 1


for i, sched in enumerate(schedulers):
    print("Feasable under sched", i, ":", len([r for r in results[sched] if r is True]))
    print("Scheduler ", i, "score:", scores[sched])

print("Interesting systems:")
for tau in interest:
    print(tau)
