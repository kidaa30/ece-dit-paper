import unittest

from Helper import myAlgebra


class TestMyAlgebra(unittest.TestCase):
    def setUp(self):
        pass

    def test_LCM(self):
        self.assertEquals(myAlgebra.lcm(2, 3), 6)
        self.assertEquals(myAlgebra.lcm(11, 121), 121)
        self.assertEquals(myAlgebra.lcm(12, 36, 30), 180)
        self.assertEquals(myAlgebra.lcmArray([12, 42]), 84)
        self.assertEquals(myAlgebra.lcmArray([2, 3, 15]), 30)
        self.assertEquals(myAlgebra.lcmArray([1, 12, 35]), 420)
        self.assertEquals(myAlgebra.lcmArray([6, 14]), 42)

    def test_EGCD(self):
        self.assertEquals(myAlgebra.egcd(9, 21), 3)
        self.assertEquals(myAlgebra.egcd(5, 125), 5)
        self.assertEquals(myAlgebra.egcd(36, 27, 45, 81), 9)

    def test_modinv(self):
        self.assertEquals(myAlgebra.modinv(3, 11), 4)
        self.assertEquals(myAlgebra.modinv(3, 5), 2)
        self.assertEquals(myAlgebra.modinv(17, 60), 53)

    def chineseRemainderTheorem(self):
        self.assertEquals(myAlgebra.chineseRemainderTheorem([2, 3, 1], [3, 4, 5]), 11)
        self.assertEquals(myAlgebra.chineseRemainderTheorem([3, 1, 4], [8, 9, 11]), 235)

    def testPrimeFactors(self):
        self.assertIn(2, myAlgebra.primeFactors(48))
        self.assertEquals(myAlgebra.primeFactors(48).count(2), 4)
        self.assertIn(3, myAlgebra.primeFactors(48))
        self.assertEquals(myAlgebra.primeFactors(48).count(3), 1)

    def testCongruence(self):
        self.assertEquals(myAlgebra.congruence([1, 0, 3, 2], [2, 3, 6, 7]), 9)
        self.assertEquals(myAlgebra.congruence([0, 0, 2, 8], [2, 8, 6, 9]), 8)
