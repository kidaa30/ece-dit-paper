from Model import algorithms
from Simulator import Simulator
from Simulator import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler
import systems


import pylab


domin_scores = {}
results = {}
NUMBER_OF_SYSTEMS = 1000
nRange = list(range(2, 6))
schedulers = [Scheduler.EDF, Scheduler.PTEDF]
names = ["EDF", "PA-EDF"]


def oneTest(taskCnt):
    domin_scores[taskCnt] = {}
    results[taskCnt] = {}
    for sched in schedulers:
        results[taskCnt][sched] = []
        domin_scores[taskCnt][sched] = 0

    for i in range(NUMBER_OF_SYSTEMS):
        print("n", taskCnt, "\t", i, "/", NUMBER_OF_SYSTEMS)
        tau = systems.generateSystemArray(1, 0, n=taskCnt, preemptionCost=-1)[0]  # 0 is implicit, 1 is constrained
        print(tau)

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
            results[taskCnt][schedClass].append(simu.success())

        assert not results[taskCnt][schedulers[0]][-1] or results[taskCnt][schedulers[1]][-1], tau

    # compute score
    for i in range(NUMBER_OF_SYSTEMS):
        for sched in schedulers:
            if results[taskCnt][sched][i]:
                undefeated = True
                for otherSched in schedulers:
                    if otherSched is not sched and results[taskCnt][otherSched][i]:
                        undefeated = False
                        break
                if undefeated:
                    domin_scores[taskCnt][sched] += 1


    # for i, sched in enumerate(schedulers):
    #     print("Feasable under sched", i, ":", len([r for r in results[taskCnt][sched] if r is True]))
    #     print("Scheduler", i, "score:", domin_scores[taskCnt][sched], "(", 100 * domin_scores[taskCnt][sched]/NUMBER_OF_SYSTEMS, "%)")

for n in nRange:
    oneTest(n)

pylab.figure()
for i, sched in enumerate(schedulers):
    dom_pct = [100 * domin_scores[n][sched] / NUMBER_OF_SYSTEMS for n in nRange]
    result = [len([r for r in results[n][sched] if r is True]) for n in nRange]
    result_pct = list(map(lambda r: 100 * r / NUMBER_OF_SYSTEMS, result))
    print("result_pct of ", names[i], result_pct)
    pylab.plot(nRange, result_pct, "o", label=names[i])

pylab.ylabel("% schedulable")
pylab.xlabel("number of tasks")
pylab.title("Schedulability of implicit systems (n = " + str(NUMBER_OF_SYSTEMS) + ")")
pylab.legend(loc=0)
pylab.axis([nRange[0] - 1, nRange[-1] + 1, 0,  100])
pylab.grid()
pylab.show()
