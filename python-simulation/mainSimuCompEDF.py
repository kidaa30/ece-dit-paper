from Model import algorithms
from Simulator import Simulator
from Simulator import Scheduler
import systems

import subprocess

resultsEDF = []
resultsCK = []
edfScore = 0
ckScore = 0

for i in range(1000):
    print i
    tau = systems.generateSystemArray(1, 1)[0]
    # tau = systems.test
    print tau

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    fpdit = algorithms.findFirstDIT(tau)
    stop = Omax + 2 * H
    if fpdit:
        stop = fpdit + H

    simuEDF = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=Scheduler.EDF(tau), abortAndRestart=False)
    simuCK = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=Scheduler.ChooseKeepEDF(tau), abortAndRestart=False)

    simuEDF.run(stopAtDeadlineMiss=True, verbose=False)
    simuCK.run(stopAtDeadlineMiss=True, verbose=False)

    resultsEDF.append(simuEDF.success())
    resultsCK.append(simuCK.success())

    # assert (not simuEDF.success()) or simuCK.success(), str(simuEDF.success()) + str(simuCK.success())
    if simuEDF.success() and not simuCK.success():
        edfScore += 1
    if simuCK.success() and not simuEDF.success():
        ckScore += 1


print "EDF", len(filter(lambda r: r is True, resultsEDF))
print "CK", len(filter(lambda r: r is True, resultsCK))

print "EDF > CK", edfScore
print "CK > EDF", ckScore
