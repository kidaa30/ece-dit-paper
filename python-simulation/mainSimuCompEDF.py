from Model import algorithms
from Simulator import Simulator
from Simulator import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler
import systems

NUMBER_OF_SYSTEMS = 2000

schedulers = [Scheduler.EDF, ChooseKeepEDF.ChooseKeepEDF]

interest = []  # system with weird property

results = {}
scores = {}
for sched in schedulers:
    results[sched] = []
    scores[sched] = 0

for i in range(NUMBER_OF_SYSTEMS):
    print(i)
    tau = systems.generateSystemArray(1, 0)[0]
    # print(tau)

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    fpdit = algorithms.findFirstDIT(tau)
    stop = Omax + 10 * H  # FIXME
    if fpdit:
        stop = fpdit + H

    for schedClass in schedulers:
        if schedClass is Scheduler.ExhaustiveFixedPriority:
            sched = schedClass(tau, 1, False)
        else:
            sched = schedClass(tau)
        simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False, drawing=False)
        simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)
        results[schedClass].append(simu.success())

    if results[schedulers[0]][-1] and not results[schedulers[1]][-1]:
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
    print("Scheduler", i, "score:", scores[sched], "(", 100*scores[sched]/NUMBER_OF_SYSTEMS, "%)")

if len(interest) > 0:
    for tau in interest:
        print(tau)
