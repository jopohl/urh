import unittest

import numpy as np

from tests.test_util import get_path_for_data_file
from urh.ainterpretation.AutoInterpretation import detect_center
from urh.cythonext.signal_functions import afp_demod


class TestCenterDetection(unittest.TestCase):
    def test_noiseless_rect(self):
        def generate_rectangular_signal(bits: str, bit_len: int):
            result = np.zeros(len(bits) * bit_len, dtype=np.float32)
            for i, bit in enumerate(bits):
                if int(bit) != 0:
                    result[i * bit_len:(i + 1) * bit_len] = np.ones(bit_len, dtype=np.int8)
            return result

        rect = generate_rectangular_signal("101010111100011", bit_len=10)
        center = detect_center(rect)
        self.assertGreaterEqual(center, 0.4)
        self.assertLessEqual(center, 0.6)

    def test_noisy_rect(self):
        data = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        rect = afp_demod(data, 0.008, 1)[5:15000]

        center = detect_center(rect)
        self.assertGreaterEqual(center, -0.0587)
        self.assertLessEqual(center, 0.02)

    def test_ask_center_detection(self):
        data = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        rect = afp_demod(data, 0.01111, 0)

        center = detect_center(rect)
        self.assertGreaterEqual(center, 0)
        self.assertLessEqual(center, 0.06)

    def test_enocean_center_detection(self):
        data = np.fromfile(get_path_for_data_file("enocean.complex"), dtype=np.complex64)
        rect = afp_demod(data, 0.0111, 0)

        center = detect_center(rect)
        self.assertGreaterEqual(center, 0.07)
        self.assertLessEqual(center, 0.5)

    def test_ask_50_center_detection(self):
        message_indices = [(0, 8000), (18000, 26000), (36000, 44000), (54000, 62000), (72000, 80000)]

        data = np.fromfile(get_path_for_data_file("ask50.complex"), dtype=np.complex64)
        rect = afp_demod(data, 0.0509, 0)

        for start, end in message_indices:
            center = detect_center(rect[start:end])
            self.assertGreaterEqual(center, 0.5326, msg="{}/{}".format(start, end))
            self.assertLessEqual(center, 0.9482, msg="{}/{}".format(start, end))
