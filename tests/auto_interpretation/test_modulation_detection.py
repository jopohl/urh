import unittest
from tests.test_util import get_path_for_data_file
from urh.ainterpretation import AutoInterpretation
import numpy as np

from urh.signalprocessing.Modulator import Modulator


class TestModulationDetection(unittest.TestCase):
    def test_fsk_detection(self):
        fsk_signal = np.fromfile(
            get_path_for_data_file("fsk.complex"), dtype=np.complex64
        )[5:15000]

        mod = AutoInterpretation.detect_modulation(
            fsk_signal, wavelet_scale=4, median_filter_order=7
        )
        self.assertEqual(mod, "FSK")

    def test_ook_detection(self):
        data = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        mod = AutoInterpretation.detect_modulation(data)
        self.assertEqual(mod, "OOK")

        data = np.fromfile(
            get_path_for_data_file("ASK_mod.complex"), dtype=np.complex64
        )
        mod = AutoInterpretation.detect_modulation(data)
        self.assertEqual(mod, "OOK")

    def test_ask50_detection(self):
        message_indices = [
            (0, 8000),
            (18000, 26000),
            (36000, 44000),
            (54000, 62000),
            (72000, 80000),
        ]
        data = np.fromfile(get_path_for_data_file("ask50.complex"), dtype=np.complex64)

        for start, end in message_indices:
            mod = AutoInterpretation.detect_modulation(data[start:end])
            self.assertEqual(mod, "ASK", msg="{}/{}".format(start, end))

    def test_psk_detection(self):
        modulator = Modulator("")
        modulator.modulation_type = "PSK"
        modulator.parameters[0] = -90
        modulator.parameters[1] = 90

        data = modulator.modulate("10101010111000")
        mod = AutoInterpretation.detect_modulation(data)
        self.assertEqual(mod, "PSK")
