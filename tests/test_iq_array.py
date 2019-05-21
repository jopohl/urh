import unittest

import numpy as np

from urh.signalprocessing.IQArray import IQArray


class TestIQArray(unittest.TestCase):
    def test_index(self):
        iq_array = IQArray(-1, np.int8, 0, 255, np.array([1, 2, 3, 4, 5, 6], dtype=np.uint8))

        self.assertEqual(iq_array[0][0], 1)
        self.assertEqual(iq_array[0][1], 2)

        self.assertEqual(iq_array[1][0], 3)
        self.assertEqual(iq_array[1][1], 4)

        self.assertEqual(iq_array[2][0], 5)
        self.assertEqual(iq_array[2][1], 6)

        self.assertEqual(iq_array[1:2][0], 3)
        self.assertEqual(iq_array[1:2][1], 4)

        self.assertEqual(iq_array[:2][0], 1)
        self.assertEqual(iq_array[:2][1], 2)
        self.assertEqual(iq_array[:2][2], 3)
        self.assertEqual(iq_array[:2][3], 4)
