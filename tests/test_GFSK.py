import os
import tempfile
import unittest

import numpy as np

from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class GFSK(unittest.TestCase):
    def test_gfsk(self):
        target_file = os.path.join(tempfile.gettempdir(), "test.complex")

        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "FSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = -10e3
        data1 = modulator.modulate([True, False, False, True, False], 9437)
        data2 = modulator.modulate([True, False, True], 9845) #, start=len(s))
        data3 = modulator.modulate([True, False, True, False], 8457) #, start=len(s))
        s = np.concatenate((data1, data2, data3))

        s.tofile(target_file)

        pa = ProtocolAnalyzer(Signal(target_file, "test", modulation="FSK"))
        pa.get_protocol_from_signal()
