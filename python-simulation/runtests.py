import unittest

from test.testSimulator import TestSimulator
from test.testMyAlgebra import TestMyAlgebra
from test.testAlgorithms import TestAlgorithms

if __name__ == '__main__':
    tests = [TestSimulator, TestMyAlgebra, TestAlgorithms]
    for test in tests:
        suite = unittest.TestLoader().loadTestsFromTestCase(test)
        unittest.TextTestRunner(verbosity=2).run(suite)
