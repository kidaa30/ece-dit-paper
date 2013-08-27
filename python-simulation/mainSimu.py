from Model import algorithms
from Simulator import Simulator
from Simulator import Scheduler
import systems

import subprocess

# tau = systems.generateSystemArray(1, 1)[0]
tau = systems.SpotlightEDFNonOptimal

Omax = max([task.O for task in tau.tasks])
H = tau.hyperPeriod()
fpdit = algorithms.findFirstDIT(tau)

print "Omax", Omax
print "H", H
print "fpdit", fpdit

stop = Omax + 2 * H
if fpdit:
    stop = fpdit + H

print "stop", stop

# scheduler = Scheduler.EDF(tau)
# scheduler = Scheduler.SpotlightEDF(tau)
scheduler = Scheduler.ChooseKeepEDF(tau)
# scheduler = Scheduler.FixedPriority(tau, [1, 2, 3])
# !!! exhaustive: set the parameters right !!!
# scheduler = Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False)
# if scheduler.foundFeasible:
#   print "found feasible priorities :", scheduler.prioArray
# else:
#   print "No feasible priorities found ! This will end badly"

simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=scheduler, abortAndRestart=False)

try:
    simu.run(stopAtDeadlineMiss=True, verbose=False)
    if simu.success():
        print "No deadline misses."
    else:
        print "Deadline miss at t=", simu.t
except AssertionError:
    print "Something went wrong ! Close the image preview to see the callback"
    raise
finally:
    simu.drawer.outImg.save("out.png")
    subprocess.Popen(['shotwell', 'out.png'])
