import unittest

import numpy as np
from urh import constants

from tests.test_util import get_path_for_data_file
from urh.ainterpretation import AutoInterpretation
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestAutoInterpretationIntegration(unittest.TestCase):
    def demodulate(self, signal_data, mod_type: str, bit_length, center, noise, tolerance, decoding=None):
        signal = Signal("", "")
        signal._fulldata = signal_data
        signal.modulation_type = signal.MODULATION_TYPES.index(mod_type)
        signal.bit_len = bit_length
        signal.qad_center = center
        signal.noise_threshold = noise
        if tolerance is not None:
            signal.tolerance = tolerance
        pa = ProtocolAnalyzer(signal)
        if decoding is not None:
            pa.decoder = decoding
        pa.get_protocol_from_signal()
        return pa.decoded_hex_str

    def test_auto_interpretation_fsk(self):
        fsk_signal = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        result = AutoInterpretation.estimate(fsk_signal)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]
        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)
        self.assertGreater(tolerance,  0)
        self.assertLessEqual(tolerance, 5)

        self.assertEqual(self.demodulate(fsk_signal, mod_type, bit_length, center, noise, tolerance)[0],
                         "aaaaaaaac626c626f4dc1d98eef7a427999cd239d3f18")

    def test_auto_interpretation_ask(self):
        ask_signal = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        result = AutoInterpretation.estimate(ask_signal)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]
        self.assertEqual(mod_type, "ASK")
        self.assertEqual(bit_length, 300)
        self.assertGreater(tolerance, 0)
        self.assertLess(tolerance, 5)

        self.assertEqual(self.demodulate(ask_signal, mod_type, bit_length, center, noise, tolerance)[0], "b25b6db6c80")

    def test_auto_interpretation_enocean(self):
        enocean_signal = np.fromfile(get_path_for_data_file("enocean.complex"), dtype=np.complex64)
        result = AutoInterpretation.estimate(enocean_signal)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]
        self.assertEqual(mod_type, "ASK")
        self.assertEqual(bit_length, 8)
        self.assertLessEqual(tolerance, 1)

        demod = self.demodulate(enocean_signal, mod_type, bit_length, center, noise, tolerance,
                                decoding=Encoding(["WSP", constants.DECODING_ENOCEAN]))
        self.assertEqual(len(demod), 3)
        self.assertEqual(demod[0], demod[2])
        self.assertEqual(demod[0], "aa9610002c1c024b")

    def test_auto_interpretation_xavax(self):
        signal = Signal(get_path_for_data_file("xavax.coco"), "")
        result = AutoInterpretation.estimate(signal.data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)
        demod = self.demodulate(signal.data, mod_type, bit_length, center, noise, tolerance)
        self.assertGreaterEqual(len(demod), 5)

        for i in range(1, len(demod)):
            self.assertTrue(demod[i].startswith("aaaaaaaa"))
