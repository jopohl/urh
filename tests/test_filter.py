import unittest

import numpy as np

from tests.QtTestCase import QtTestCase
from urh.signalprocessing.Filter import Filter


class TestFilter(QtTestCase):
    def test_fir_filter(self):
        input_signal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 42], dtype=np.complex64)
        filter_taps = [0.25, 0.25, 0.25, 0.25]

        fir_filter = Filter("my_filter", filter_taps)

        filtered_signal = fir_filter.apply_fir_filter(input_signal)
        expected_filtered_signal = np.array([0.25, 0.75, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 16.5], dtype=np.complex64)

        self.assertTrue(np.array_equal(filtered_signal, expected_filtered_signal))

if __name__ == '__main__':
    unittest.main()
