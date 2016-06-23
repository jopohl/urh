
# (0, 32), (0, 80), (41, 56), (43, 56), (63, 76), (64, 76), (79, 116), (103, 116), (104, 116), (104, 336), (106, 124), (120, 128), (189, 208), (191, 208), (192, 208), (197, 212), (198, 212), (199, 212), (200, 212), (231, 240), (243, 264), (247, 264), (248, 264), (396, 416)
import unittest

from urh.signalprocessing.Interval import Interval


class TestInterval(unittest.TestCase):
    def test_find_common_interval(self):
        i1 = Interval(0, 32)
        i2 = Interval(0, 80)
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