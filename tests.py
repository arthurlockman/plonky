import unittest
from genjam import Measure, Phrase


class MutationTests(unittest.TestCase):

    def test_measure_reverse(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 0
        m[1] = 1
        m[2] = 2
        m[3] = 3
        Measure.reverse(m)

        self.assertEqual(m[0], 3)
        self.assertEqual(m[1], 2)
        self.assertEqual(m[2], 1)
        self.assertEqual(m[3], 0)

    def test_measure_rotate(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 0
        m[1] = 1
        m[2] = 2
        m[3] = 3
        Measure._rotate(m, 1)

        self.assertEqual(m[0], 3)
        self.assertEqual(m[1], 0)
        self.assertEqual(m[2], 1)
        self.assertEqual(m[3], 2)

        Measure._rotate(m, 1)

        self.assertEqual(m[0], 2)
        self.assertEqual(m[1], 3)
        self.assertEqual(m[2], 0)
        self.assertEqual(m[3], 1)

    def test_measure_invert(self):
        m = Measure(4, 4)
        m.initialize()
        m[0] = 0
        m[1] = 1
        m[2] = 2
        m[3] = 3
        Measure.invert(m)

        self.assertEqual(m[0], 15)
        self.assertEqual(m[1], 14)
        self.assertEqual(m[2], 13)
        self.assertEqual(m[3], 12)

    def test_measure_ascending(self):
        m = Measure(8, 4)
        m.initialize()
        m[0] = 9
        m[1] = 7
        m[2] = 0
        m[3] = 5
        m[4] = 7
        m[5] = 15
        m[6] = 15
        m[7] = 0
        Measure.sort_ascending(m)

        self.assertEqual(m[0], 5)
        self.assertEqual(m[1], 7)
        self.assertEqual(m[2], 0)
        self.assertEqual(m[3], 7)
        self.assertEqual(m[4], 9)
        self.assertEqual(m[5], 15)
        self.assertEqual(m[6], 15)
        self.assertEqual(m[7], 0)

    def test_measure_descending(self):
        m = Measure(8, 4)
        m.initialize()
        m[0] = 9
        m[1] = 7
        m[2] = 0
        m[3] = 5
        m[4] = 7
        m[5] = 15
        m[6] = 15
        m[7] = 0
        Measure.sort_descending(m)

        self.assertEqual(m[0], 9)
        self.assertEqual(m[1], 7)
        self.assertEqual(m[2], 0)
        self.assertEqual(m[3], 7)
        self.assertEqual(m[4], 5)
        self.assertEqual(m[5], 15)
        self.assertEqual(m[6], 15)
        self.assertEqual(m[7], 0)
