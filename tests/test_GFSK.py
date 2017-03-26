import unittest

import numpy as np

from tests import utils_testing
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal

utils_testing.write_settings()

class GFSK(unittest.TestCase):
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
