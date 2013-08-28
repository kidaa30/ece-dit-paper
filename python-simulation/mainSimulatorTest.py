from Simulator import Simulator, Scheduler
from Model import algorithms
import systems

import unittest


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = None

    def launchSimulator(self, tau, sched):
        Omax = max([task.O for task in tau.tasks])
        H = tau.hyperPeriod()
        fpdit = algorithms.findFirstDIT(tau)
        stop = Omax + 2 * H
        if fpdit:
            stop = fpdit + H

        self.simulator = Simulator.Simulator(tau, stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False)
        self.simulator.run()

    def test_Meumeu(self):
        tau = systems.Meumeu
        sched = Scheduler.EDF(tau)
        self.launchSimulator(tau, sched)
        self.assertTrue(self.simulator.success())

    def test_EDFNonOptimal(self):
        tau = systems.EDFNonOptimal
        edf = Scheduler.EDF(tau)
        spot = Scheduler.SpotlightEDF(tau)
        self.launchSimulator(tau, edf)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, spot)
        self.assertTrue(self.simulator.success())

    def test_SpotlightEDFNonOptimal(self):
        tau = systems.SpotlightEDFNonOptimal
        spot = Scheduler.SpotlightEDF(tau)
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, spot)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())

    def test_PreemptNoIdle(self):
        # difficult case where idling seems preferable but leads to unfeasibility
        tau = systems.PreemptNoIdle
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())

    def test_MustIdle(self):
        # unfeasible by non-idling algorithms
        tau = systems.MustIdle
        edf = Scheduler.EDF(tau)
        spot = Scheduler.SpotlightEDF(tau)
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, edf)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, spot)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())

    def test_DPOnly(self):
        tau = systems.DPOnly
        tau = systems.MustIdle
        edf = Scheduler.EDF(tau)
        spot = Scheduler.SpotlightEDF(tau)
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, edf)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, spot)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())

    def test_KeepForLater(self):
        tau = systems.KeepForLater
        edf = Scheduler.EDF(tau)
        spot = Scheduler.SpotlightEDF(tau)
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, edf)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, spot)
        self.assertTrue(not self.simulator.success())
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())

    def test_SamePriorityHijinks(self):
        tau = systems.SamePriorityHijinks
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())
        tau = systems.SamePriorityHijinks2
        self.launchSimulator(tau, cak)
        self.assertTrue(self.simulator.success())

    def test_CKEDFKNonOptimal(self):
        tau = systems.CKEDFNonOptimal
        cak = Scheduler.ChooseKeepEDF(tau)
        self.launchSimulator(tau, cak)
        self.assertTrue(not self.simulator.success())

if __name__ == '__main__':
    unittest.main()
