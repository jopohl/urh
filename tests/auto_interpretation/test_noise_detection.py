import unittest

import numpy as np

from urh.ainterpretation.AutoInterpretation import detect_noise_level
from tests.test_util import get_path_for_data_file


class TestNoiseDetection(unittest.TestCase):
    def test_for_fsk_signal(self):
        data = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        noise_level = detect_noise_level(np.abs(data), k=2)
        self.assertGreaterEqual(noise_level, 0.0005)
        self.assertLessEqual(noise_level, 0.009)

    def test_for_ask_signal(self):
        data = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        noise_level = detect_noise_level(np.abs(data), k=2)
        self.assertGreaterEqual(noise_level, 0.0111)
        self.assertLessEqual(noise_level, 0.043)

    def test_for_enocean_ask_signal(self):
        data = np.fromfile(get_path_for_data_file("enocean.complex"), dtype=np.complex64)
        noise_level = detect_noise_level(np.abs(data), k=2)
        self.assertGreaterEqual(noise_level, 0.01)
        self.assertLessEqual(noise_level, 0.28)

    def test_for_noiseless_signal(self):
        data = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)[0:17639]
        noise_level = detect_noise_level(np.abs(data), k=2)
        self.assertEqual(noise_level, 0)
