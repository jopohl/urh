import unittest

import numpy

from urh.signalprocessing.Modulator import Modulator


class GFSK(unittest.TestCase):
    def test_gfsk(self):
        modulator = Modulator("gfsk")
        modulator.modulation_type_str = "GFSK"
        modulator.samples_per_bit = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = 10e3
        modulator.modulate([True, False, False, True, False], 9437)
        s = modulator.modulated_samples
        modulator.modulate([True, False, True], 8457, start=len(s))
        s = numpy.concatenate((s, modulator.modulated_samples))

        s.tofile("/tmp/test.complex")
