import math
import unittest

import numpy as np

from tests.test_util import get_path_for_data_file
from urh.ainterpretation.AutoInterpretation import detect_center


class TestCenterDetection(unittest.TestCase):
    def test_noiseless_rect(self):
        def generate_rectangular_signal(bits: str, bit_len: int):
            result = np.zeros(len(bits) * bit_len, dtype=np.int8)
            for i, bit in enumerate(bits):
                if int(bit) != 0:
                    result[i * bit_len:(i + 1) * bit_len] = np.ones(bit_len, dtype=np.int8)
            return result

        rect = generate_rectangular_signal("101010111100011", bit_len=10)
        center = detect_center(rect)
        self.assertEqual(center, 0.5)

    def test_noisy_rect_non_weak_only(self):
        rect = np.fromfile(get_path_for_data_file("fsk-demodulated-non-weak-only.complex"), dtype=np.float32)
        center = detect_center(rect)
        self.assertTrue(math.isclose(center, -0.03, abs_tol=1e-2))

    def test_noisy_rect(self):
        rect = np.fromfile(get_path_for_data_file("fsk-demodulated.complex"), dtype=np.float32)
        center = detect_center(rect)
        assert math.isclose(center, -0.03, abs_tol=1e-2)

    def test_ask_center_detection(self):
        rect = np.fromfile(get_path_for_data_file("ask-demodulated.complex"), dtype=np.float32)
        center = detect_center(rect)
        self.assertGreaterEqual(center, 0)
        self.assertLessEqual(center, 0.0035)

    def test_enocean_center_detection(self):
        rect = np.fromfile(get_path_for_data_file("enocean-demodulated.complex"), dtype=np.float32)
        center = detect_center(rect)
        self.assertGreaterEqual(center, 0.07)
        self.assertLessEqual(center, 0.2246)
