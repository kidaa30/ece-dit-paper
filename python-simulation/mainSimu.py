from Model import algorithms
from Simulator import Simulator
from Simulator.Scheduler import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler
import systems

import subprocess
import sys

# tau = systems.generateSystemArray(1, 0)[0]
tau = systems.LongTransitive2

Omax = max([task.O for task in tau.tasks])
H = tau.hyperPeriod()
fpdit = algorithms.findFirstDIT(tau)

print(("Omax", Omax))
print(("H", H))
print(("fpdit", fpdit))
print(("U", tau.systemUtilization()))

stop = Omax + 10 * H
# if fpdit:
#     stop = fpdit + H

print(("stop", stop))

# scheduler = Scheduler.EDF(tau)
# scheduler = Scheduler.SpotlightEDF(tau)
# scheduler = ChooseKeepEDF.ChooseKeepEDF(tau)
scheduler = Scheduler.PTEDF(tau)
# scheduler = PALLF.PALLF(tau)
# scheduler = Scheduler.ArbitraryScheduler(tau, systems.mpanaSchedule)
# scheduler = LBLScheduler.LBLEDF(tau)

# scheduler = Scheduler.FixedPriority(tau, [1, 2, 3])
# !!! exhaustive: set the parameters right !!!
# scheduler = Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False)
# if scheduler.foundFeasible:
#   print "found feasible priorities :", scheduler.prioArray
# else:
#   print "No feasible priorities found !"

simu = Simulator.Simulator(tau, stop=1000, nbrCPUs=1, scheduler=scheduler, abortAndRestart=False, verbose=True)

try:
    simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)
    if simu.success():
        print("Success.")
    else:
        print("Failure.")
except AssertionError:
    print("Something went wrong ! Close the image preview to see the stack trace")
    raise
finally:
    if "linux" in sys.platform:
        simu.drawer.outImg.save("out.png")
        subprocess.Popen(['shotwell', 'out.png'])
    elif "win" in sys.platform:
        simu.drawer.outImg.show()
