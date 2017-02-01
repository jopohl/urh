import copy
import unittest

import matplotlib.pyplot as plt
import numpy as np

from urh.signalprocessing.Modulator import Modulator
from urh.cythonext import signalFunctions


class PlotTests(unittest.TestCase):
    def test_plot(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "GFSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = 10e3
        modulator.carrier_freq_hz = 15e3
        modulator.carrier_phase_deg = 90


        modulator.modulate([True, False, True, False, False], 77)
        data = copy.deepcopy(modulator.modulated_samples)
        modulator.modulate([False, True, True, True, True, False, True], 100, start=len(data))
        data = np.concatenate((data, modulator.modulated_samples))

        plt.subplot(2, 1, 1)
        axes = plt.gca()
        axes.set_ylim([-2,2])
        plt.plot(data.real)
        plt.title("Modulated Wave")

        plt.subplot(2, 1, 2)
        qad = signalFunctions.afp_demod(np.ascontiguousarray(data), 0, 1)
        plt.plot(qad)
        plt.title("Quad Demod")

        plt.show()