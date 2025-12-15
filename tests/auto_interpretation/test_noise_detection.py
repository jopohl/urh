import unittest

import numpy as np

from urh.ainterpretation.AutoInterpretation import detect_noise_level
from tests.test_util import get_path_for_data_file
from urh.signalprocessing.Signal import Signal


class TestNoiseDetection(unittest.TestCase):
    def test_for_fsk_signal(self):
        data = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        noise_level = detect_noise_level(np.abs(data))
        self.assertGreaterEqual(noise_level, 0.0005)
        self.assertLessEqual(noise_level, 0.009)

    def test_for_ask_signal(self):
        data = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        noise_level = detect_noise_level(np.abs(data))
        self.assertGreaterEqual(noise_level, 0.0110)
        self.assertLessEqual(noise_level, 0.043)

    def test_for_fsk_signal_with_little_noise_before_and_after(self):
        data = np.concatenate(
            (
                np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)[
                    -1000:
                ],
                np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)[
                    0:18800
                ],
            )
        )
        noise_level = detect_noise_level(np.abs(data))
        self.assertGreaterEqual(noise_level, 0.0005)
        self.assertLessEqual(noise_level, 0.009)

    def test_for_enocean_ask_signal(self):
        data = np.fromfile(
            get_path_for_data_file("enocean.complex"), dtype=np.complex64
        )
        noise_level = detect_noise_level(np.abs(data))
        self.assertGreaterEqual(noise_level, 0.01)
        self.assertLessEqual(noise_level, 0.28)

    def test_for_noiseless_signal(self):
        data = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)[
            0:17639
        ]
        noise_level = detect_noise_level(np.abs(data))
        self.assertEqual(noise_level, 0)

    def test_multi_messages_different_rssi(self):
        data = Signal(
            get_path_for_data_file("multi_messages_different_rssi.coco"), ""
        ).iq_array.data
        noise_level = detect_noise_level(np.abs(data))
        self.assertGreater(noise_level, 0.001)
        self.assertLess(noise_level, 0.002)

    def test_for_psk_signal(self):
        data = Signal(get_path_for_data_file("psk_generated.complex"), "").iq_array.data
        noise_level = detect_noise_level(np.abs(data))
        self.assertGreater(noise_level, 0.0067)
        self.assertLessEqual(noise_level, 0.0081)

    def test_for_noisy_fsk_15db_signal(self):
        data = Signal(get_path_for_data_file("FSK15.complex"), "").iq_array.data
        noise_level = detect_noise_level(np.abs(data))
        self.assertEqual(noise_level, 0)
