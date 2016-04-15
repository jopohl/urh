import copy
import unittest

import matplotlib.pyplot as plt
import numpy as np

from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.cythonext import signalFunctions

class GFSK(unittest.TestCase):
    def test_plot(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "GFSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = -10e3


        modulator.modulate([True, False, True, False], 77)
        data = copy.deepcopy(modulator.modulated_samples)
        modulator.modulate([False, True, True, False, True], 100, start=len(data))
        data = np.concatenate((data, modulator.modulated_samples))

        plt.subplot(2, 1, 1)
        plt.plot(data.real)
        plt.title("Modulated Wave")

        plt.subplot(2, 1, 2)
        qad =  signalFunctions.afp_demod(np.ascontiguousarray(data), 0, 1)
        plt.plot(qad)
        plt.title("Quad Demod")

        plt.show()


    def test_gfsk(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "FSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = -10e3
        modulator.modulate([True, False, False, True, False], 9437)
        s = modulator.modulated_samples
        modulator.modulate([True, False, True], 9845) #, start=len(s))
        s = np.concatenate((s, modulator.modulated_samples))
        modulator.modulate([True, False, True, False], 8457) #, start=len(s))
        s = np.concatenate((s, modulator.modulated_samples))

        s.tofile("/tmp/test.complex")

        pa = ProtocolAnalyzer(Signal("/tmp/test.complex", "test", modulation="FSK"))
        pa.get_protocol_from_signal()