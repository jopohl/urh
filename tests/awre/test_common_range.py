import unittest

from urh.awre.CommonRange import CommonRange


class TestCommonRange(unittest.TestCase):
    def test_ensure_not_overlaps(self):
        test_range = CommonRange(start=4, length=8, value="12345678")
        self.assertEqual(test_range.end, 11)

        # no overlapping
        self.assertEqual(test_range, test_range.ensure_not_overlaps(0, 3)[0])
        self.assertEqual(test_range, test_range.ensure_not_overlaps(20, 24)[0])

        # overlapping on left
        result = test_range.ensure_not_overlaps(2, 6)[0]
        self.assertEqual(result.start, 6)
        self.assertEqual(result.end, 11)

        # overlapping on right
        result = test_range.ensure_not_overlaps(6, 14)[0]
        self.assertEqual(result.start, 4)
        self.assertEqual(result.end, 5)

        # full overlapping
        self.assertEqual(len(test_range.ensure_not_overlaps(3, 14)), 0)

        # overlapping in the middle
        result = test_range.ensure_not_overlaps(6, 9)
        self.assertEqual(len(result), 2)
        left, right = result[0], result[1]
        self.assertEqual(left.start, 4)
        self.assertEqual(left.end, 5)
        self.assertEqual(right.start, 10)
        self.assertEqual(right.end, 11)
