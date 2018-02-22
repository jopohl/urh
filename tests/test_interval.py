import unittest

from urh.signalprocessing.Interval import Interval


class TestInterval(unittest.TestCase):
    def test_is_overlapping(self):
        i1 = Interval(40, 64)
        i2 = Interval(64, 104)
        self.assertFalse(i1.overlaps_with(i2))
        self.assertFalse(i2.overlaps_with(i1))
        self.assertTrue(i1.overlaps_with(i1))
        self.assertTrue(i2.overlaps_with(i2))

    def test_find_common_interval(self):
        i1 = Interval(0, 32)
        self.assertEqual(i1, i1.find_common_interval(i1))

        i2 = Interval(0, 80)
        self.assertEqual(i2, i2.find_common_interval(i2))

        expected_result = Interval(0, 32)
        self.assertTrue(i1.overlaps_with(i2))
        self.assertTrue(i2.overlaps_with(i1))
        self.assertEqual(i1.find_common_interval(i2), expected_result)
        self.assertEqual(i2.find_common_interval(i1), expected_result)

        i1 = Interval(41, 56)
        i2 = Interval(43, 56)
        expected_result = Interval(43, 56)
        self.assertTrue(i1.overlaps_with(i2))
        self.assertTrue(i2.overlaps_with(i1))
        self.assertEqual(i1.find_common_interval(i2), expected_result)
        self.assertEqual(i2.find_common_interval(i1), expected_result)

    def test_sort(self):
        i1 = Interval(0, 10)
        i2 = Interval(0, 20)
        i3 = Interval(0, 30)

        s = {i1, i2, i3}
        self.assertEqual(max(s), i3)
        self.assertEqual(sorted(s)[-1], i3)
