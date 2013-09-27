import unittest

from test.testSimulator import TestSimulator

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulator)
    unittest.TextTestRunner(verbosity=2).run(suite)
