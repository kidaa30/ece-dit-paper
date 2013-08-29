from Simulator import Simulator, Scheduler, ChooseKeepEDF, PALLF
from Model import algorithms
import systems

import unittest


class TestSimulator(unittest.TestCase):
    def setUp(self):
        pass

    def checkResult(self, tau, sched, expectedResult):
        Omax = max([task.O for task in tau.tasks])
        H = tau.hyperPeriod()
        fpdit = algorithms.findFirstDIT(tau)
        stop = Omax + 2 * H
        if fpdit:
            stop = fpdit + H

        simulator = Simulator.Simulator(tau, stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False)
        simulator.run()
        self.assertIs(simulator.success(), expectedResult)

    def test_AtomicPreemptionCost(self):
        tau = systems.AtomicPreemptionCost
        self.checkResult(tau, Scheduler.EDF(tau), True)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

        sim = Simulator.Simulator(tau, stop=5, nbrCPUs=1, scheduler=Scheduler.EDF(tau), abortAndRestart=False)
        sim.run()
        self.assertEquals(sim.t, 6)
        blockedJob = sim.mostPrioritaryJob()
        self.assertIsNotNone(blockedJob)
        self.assertEquals(blockedJob.computation, 0)

    def test_Meumeu(self):
        tau = systems.Meumeu
        self.checkResult(tau, Scheduler.EDF(tau), True)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_EDFNonOptimal(self):
        tau = systems.EDFNonOptimal
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_SpotlightEDFNonOptimal(self):
        tau = systems.SpotlightEDFNonOptimal
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_PreemptNoIdle(self):
        # difficult case where idling seems preferable but leads to unfeasibility
        tau = systems.PreemptNoIdle
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_MustIdle(self):
        # unfeasible by non-idling algorithms
        tau = systems.MustIdle
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_DPOnly(self):
        tau = systems.DPOnly
        tau = systems.MustIdle
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_KeepForLater(self):
        tau = systems.KeepForLater
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_SamePriorityHijinks(self):
        tau = systems.SamePriorityHijinks
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_SamePriorityHijinks2(self):
        tau2 = systems.SamePriorityHijinks2
        self.checkResult(tau2, ChooseKeepEDF.ChooseKeepEDF(tau2), True)
        self.checkResult(tau2, PALLF.PALLF(tau2), True)

    def test_SamePriorityHijinks3(self):
        tau3 = systems.SamePriorityHijinks3
        self.checkResult(tau3, ChooseKeepEDF.ChooseKeepEDF(tau3), True)
        self.checkResult(tau3, PALLF.PALLF(tau3), True)

    def test_CKEDFKNonOptimal(self):
        tau = systems.CKEDFNonOptimal
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), False)
        self.checkResult(tau, PALLF.PALLF(tau), True)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulator)
    unittest.TextTestRunner(verbosity=2).run(suite)
