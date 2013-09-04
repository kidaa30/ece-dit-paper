from .Model import algorithms
from .Simulator import Simulator
from .Simulator import Scheduler, ChooseKeepEDF, PALLF
from . import systems

import subprocess

resultsEDF = []
resultsCK = []
resultsPALLF = []

edfScore = 0
ckScore = 0
pallfScore = 0

for i in range(1000):
    print(i)
    tau = systems.generateSystemArray(1, 1)[0]
    # tau = systems.test
    print(tau)

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    fpdit = algorithms.findFirstDIT(tau)
    stop = Omax + 2 * H
    if fpdit:
        stop = fpdit + H

    simuEDF = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=Scheduler.EDF(tau), abortAndRestart=False)
    simuCK = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=ChooseKeepEDF.ChooseKeepEDF(tau), abortAndRestart=False)
    simuPALLF = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=PALLF.PALLF(tau), abortAndRestart=False)

    simuEDF.run(stopAtDeadlineMiss=True)
    simuCK.run(stopAtDeadlineMiss=True)
    # simuPALLF.run(stopAtDeadlineMiss=True)

    resultsEDF.append(simuEDF.success())
    resultsCK.append(simuCK.success())
    # resultsPALLF.append(simuPALLF.success())

    # assert (not simuEDF.success()) or simuCK.success(), str(simuEDF.success()) + str(simuCK.success())
    if simuEDF.success() and not simuCK.success() and not simuPALLF.success():
        edfScore += 1
#    if simuCK.success() and not simuEDF.success() and not simuPALLF.success():
    if simuCK.success() and not simuEDF.success():
        ckScore += 1
    # if simuPALLF.success() and not simuEDF.success() and not simuCK.success():
    #     pallfScore += 1


print(("EDF fs", len([r for r in resultsEDF if r is True])))
print(("CK fs", len([r for r in resultsCK if r is True])))
print(("PALLF fs", len([r for r in resultsPALLF if r is True])))

print(("EDF is best", edfScore))
print(("CK is best", ckScore))
print(("PALLF is best", pallfScore))
