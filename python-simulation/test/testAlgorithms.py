import unittest

from Model import algorithms as algo
from Model.Task import Task, TaskSystem


class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        pass

    def test_Trivial(self):
        tasks = []
        tasks.append(Task(0, 1, 3, 6))
        tasks.append(Task(0, 1, 3, 3))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.completedJobCount(tau.tasks[0], 15, 25), 1)
        self.assertEquals(algo.completedJobCount(tau.tasks[0], 0, 33), 6)
        self.assertEquals(algo.completedJobCount(tau.tasks[1], 0, 33), 11)
        self.assertEquals(algo.findBusyPeriod(tau), 2)
        self.assertEquals(algo.findFirstDIT(tau), 3)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertTrue(algo.dbfTest(tau))

    def test_influenceDeadlineOnDIT(self):
        tasks = []
        tasks.append(Task(0, 1, 1, 6))
        tasks.append(Task(0, 1, 1, 3))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.findBusyPeriod(tau),  2)
        self.assertEquals(algo.findFirstDIT(tau), 1)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertFalse(algo.dbfTest(tau))

    def test_congruenceEdgeCase(self):
        tasks = []
        tasks.append(Task(0, 1, 2, 2))
        tasks.append(Task(0, 1, 3, 3))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.findBusyPeriod(tau), 2)
        self.assertEquals(algo.findFirstDIT(tau), 6)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertTrue(algo.dbfTest(tau))

    def test_asynchronous1(self):
        tasks = []
        tasks.append(Task(5, 1, 1, 3))
        tasks.append(Task(0, 4, 4, 8))
        tau = TaskSystem(tasks)
        # No busy period test as it does not make sense in asynchronous system
        self.assertEquals(algo.findFirstPeriodicDIT(tau), 6)
        self.assertEquals(algo.findSynchronousInstant(tau), 8)
        self.assertTrue(algo.dbfTest(tau))

    def test_asynchronous2(self):
        tasks = []
        tasks.append(Task(0, 1, 4, 6))
        tasks.append(Task(2, 1, 3, 6))
        tasks.append(Task(10, 1, 1, 2))
        tau = TaskSystem(tasks)
        assert algo.findFirstPeriodicDIT(tau) == 11
        assert algo.findSynchronousInstant(tau) is None
