import unittest

import numpy as np

from tests.test_util import get_path_for_data_file
from urh.ainterpretation.AutoInterpretation import detect_center
from urh.cythonext.signal_functions import afp_demod

from urh.signalprocessing.Filter import Filter, FilterType
from urh.signalprocessing.Signal import Signal


class TestCenterDetection(unittest.TestCase):
    def test_noiseless_rect(self):
        def generate_rectangular_signal(bits: str, bit_len: int):
            result = np.zeros(len(bits) * bit_len, dtype=np.float32)
            for i, bit in enumerate(bits):
                if int(bit) != 0:
                    result[i * bit_len : (i + 1) * bit_len] = np.ones(
                        bit_len, dtype=np.int8
                    )
            return result

        rect = generate_rectangular_signal("101010111100011", bit_len=10)
        center = detect_center(rect)
        self.assertGreaterEqual(center, 0.4)
        self.assertLessEqual(center, 0.6)

    def test_noisy_rect(self):
        data = Signal(get_path_for_data_file("fsk.complex")).iq_array.data
        rect = afp_demod(data, 0.008, "FSK", 2)[5:15000]

        center = detect_center(rect)
        self.assertGreaterEqual(center, -0.0587)
        self.assertLessEqual(center, 0.02)

    def test_ask_center_detection(self):
        data = Signal(get_path_for_data_file("ask.complex")).iq_array.data
        rect = afp_demod(data, 0.01111, "ASK", 2)

        center = detect_center(rect)
        self.assertGreaterEqual(center, 0)
        self.assertLessEqual(center, 0.06)

    def test_enocean_center_detection(self):
        data = Signal(get_path_for_data_file("enocean.complex")).iq_array.data
        rect = afp_demod(data, 0.05, "ASK", 2)
        messages = [rect[2107:5432], rect[20428:23758], rect[44216:47546]]

        for i, msg in enumerate(messages):
            center = detect_center(msg)
            self.assertGreaterEqual(center, 0.04, msg=str(i))
            self.assertLessEqual(center, 0.072, msg=str(i))

    def test_ask_50_center_detection(self):
        message_indices = [
            (0, 8000),
            (18000, 26000),
            (36000, 44000),
            (54000, 62000),
            (72000, 80000),
        ]

        data = Signal(get_path_for_data_file("ask50.complex")).iq_array.data
        rect = afp_demod(data, 0.0509, "ASK", 2)

        for start, end in message_indices:
            center = detect_center(rect[start:end])
            self.assertGreaterEqual(center, 0.4, msg="{}/{}".format(start, end))
            self.assertLessEqual(center, 0.65, msg="{}/{}".format(start, end))

    def test_homematic_center_detection(self):
        data = Signal(get_path_for_data_file("homematic.complex32s"), "").iq_array.data
        rect = afp_demod(data, 0.0012, "FSK", 2)

        msg1 = rect[17719:37861]
        msg2 = rect[70412:99385]

        center1 = detect_center(msg1)
        self.assertGreaterEqual(center1, -0.1285)
        self.assertLessEqual(center1, -0.0413)

        center2 = detect_center(msg2)
        self.assertGreaterEqual(center2, -0.1377)
        self.assertLessEqual(center2, -0.0367)

    def test_noised_homematic_center_detection(self):
        data = Signal(
            get_path_for_data_file("noised_homematic.complex"), ""
        ).iq_array.data
        rect = afp_demod(data, 0.0, "FSK", 2)

        center = detect_center(rect)

        self.assertGreater(center, -0.0148)
        self.assertLess(center, 0.0024)

    def test_fsk_15db_center_detection(self):
        data = Signal(get_path_for_data_file("FSK15.complex"), "").iq_array.data
        rect = afp_demod(data, 0, "FSK", 2)
        center = detect_center(rect)
        self.assertGreaterEqual(center, -0.1979)
        self.assertLessEqual(center, 0.1131)

    def test_fsk_10db_center_detection(self):
        data = Signal(get_path_for_data_file("FSK10.complex"), "").iq_array.data
        rect = afp_demod(data, 0, "FSK", 2)
        center = detect_center(rect)
        self.assertGreaterEqual(center, -0.1413)
        self.assertLessEqual(center, 0.05)

    def test_fsk_live_capture(self):
        data = Signal(get_path_for_data_file("fsk_live.coco"), "").iq_array.data

        n = 10
        moving_average_filter = Filter(
            [1 / n for _ in range(n)], filter_type=FilterType.moving_average
        )
        filtered_data = moving_average_filter.apply_fir_filter(data.flatten()).view(
            np.float32
        )
        filtered_data = filtered_data.reshape((len(filtered_data) // 2, 2))

        rect = afp_demod(filtered_data, 0.0175, "FSK", 2)
        center = detect_center(rect)
        self.assertGreaterEqual(center, -0.0148, msg="Filtered")
        self.assertLessEqual(center, 0.01, msg="Filtered")

        rect = afp_demod(data, 0.0175, "FSK", 2)
        center = detect_center(rect)
        self.assertGreaterEqual(center, -0.02, msg="Original")
        self.assertLessEqual(center, 0.01, msg="Original")
