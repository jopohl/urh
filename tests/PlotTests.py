import copy
import unittest

import matplotlib.pyplot as plt
import numpy as np

from urh.signalprocessing.Modulator import Modulator
from urh.cythonext import signal_functions
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from tests.utils_testing import get_path_for_data_file


class PlotTests(unittest.TestCase):
    def test_plot(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type = "GFSK"
        modulator.samples_per_symbol = 100
        modulator.sample_rate = 1e6
        modulator.parameters[1] = 20e3
        modulator.parameters[0] = 10e3
        modulator.carrier_freq_hz = 15e3
        modulator.carrier_phase_deg = 90

        modulated_samples = modulator.modulate([True, False, True, False, False], 77)
        data = copy.deepcopy(modulated_samples)
        modulated_samples = modulator.modulate(
            [False, True, True, True, True, False, True], 100, start=len(data)
        )
        data = np.concatenate((data, modulated_samples))

        plt.subplot(2, 1, 1)
        axes = plt.gca()
        axes.set_ylim([-2, 2])
        plt.plot(data.real)
        plt.title("Modulated Wave")

        plt.subplot(2, 1, 2)
        qad = signal_functions.afp_demod(np.ascontiguousarray(data), 0, "FSK", 2)
        plt.plot(qad)
        plt.title("Quad Demod")

        plt.show()

    def test_carrier_auto_detect(self):
        signal = Signal(get_path_for_data_file("wsp.complex"), "test")
        signal.modulation_type = "ASK"
        signal.noise_threshold = 0.035
        signal.center = 0.0245
        signal.samples_per_symbol = 25
        pa = ProtocolAnalyzer(signal)
        pa.get_protocol_from_signal()
        start, num_samples = pa.get_samplepos_of_bitseq(
            0, 0, 0, 999999, include_pause=False
        )

        print("-----------")
        print(
            signal.estimate_frequency(start, end=start + num_samples, sample_rate=2e6)
        )
