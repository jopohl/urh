import unittest

import numpy as np

from tests.auto_interpretation.auto_interpretation_test_util import demodulate
from tests.test_util import get_path_for_data_file
from urh import settings
from urh.ainterpretation import AutoInterpretation
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.Signal import Signal


class TestAutoInterpretationIntegration(unittest.TestCase):
    def test_auto_interpretation_fsk(self):
        fsk_signal = np.fromfile(
            get_path_for_data_file("fsk.complex"), dtype=np.float32
        )
        result = AutoInterpretation.estimate(fsk_signal)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )
        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)
        self.assertGreater(tolerance, 0)
        self.assertLessEqual(tolerance, 5)

        self.assertEqual(
            demodulate(fsk_signal, mod_type, bit_length, center, noise, tolerance)[0],
            "aaaaaaaac626c626f4dc1d98eef7a427999cd239d3f18",
        )

    def test_auto_interpretation_ask(self):
        ask_signal = np.fromfile(
            get_path_for_data_file("ask.complex"), dtype=np.float32
        )
        result = AutoInterpretation.estimate(ask_signal)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )
        self.assertEqual(mod_type, "ASK")
        self.assertEqual(bit_length, 300)
        self.assertGreater(tolerance, 0)
        self.assertLessEqual(tolerance, 6)

        self.assertEqual(
            demodulate(ask_signal, mod_type, bit_length, center, noise, tolerance)[0],
            "b25b6db6c80",
        )

    def test_auto_interpretation_overshoot_ook(self):
        data = Signal(get_path_for_data_file("ook_overshoot.complex16s"), "").iq_array
        result = AutoInterpretation.estimate(data)
        self.assertEqual(result["modulation_type"], "ASK")
        self.assertEqual(result["bit_length"], 500)

    def test_auto_interpretation_enocean(self):
        enocean_signal = np.fromfile(
            get_path_for_data_file("enocean.complex"), dtype=np.float32
        )
        result = AutoInterpretation.estimate(enocean_signal)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )
        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(center, 0.0077)
        self.assertLessEqual(center, 0.0465)
        self.assertLessEqual(tolerance, 5)
        self.assertEqual(bit_length, 40)

        demod = demodulate(
            enocean_signal,
            mod_type,
            bit_length,
            center,
            noise,
            tolerance,
            decoding=Encoding(["WSP", settings.DECODING_ENOCEAN]),
        )
        self.assertEqual(len(demod), 3)
        self.assertEqual(demod[0], demod[2])
        self.assertEqual(demod[0], "aa9610002c1c024b")

    def test_auto_interpretation_xavax(self):
        signal = Signal(get_path_for_data_file("xavax.coco"), "")
        result = AutoInterpretation.estimate(signal.iq_array.data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)
        demod = demodulate(
            signal.iq_array.data, mod_type, bit_length, center, noise, tolerance
        )
        self.assertGreaterEqual(len(demod), 5)

        for i in range(1, len(demod)):
            self.assertTrue(demod[i].startswith("aaaaaaaa"))

    def test_auto_interpretation_elektromaten(self):
        data = Signal(get_path_for_data_file("elektromaten.complex16s"), "").iq_array
        result = AutoInterpretation.estimate(data)

        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "ASK")
        self.assertEqual(bit_length, 600)

        demodulated = demodulate(
            data, mod_type, bit_length, center, noise, tolerance, pause_threshold=8
        )
        self.assertEqual(len(demodulated), 11)
        for i in range(11):
            self.assertTrue(demodulated[i].startswith("8"))

    def test_auto_interpretation_homematic(self):
        data = Signal(get_path_for_data_file("homematic.complex32s"), "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)

        demodulated = demodulate(data, mod_type, bit_length, center, noise, tolerance)
        self.assertEqual(len(demodulated), 2)
        for i in range(2):
            self.assertTrue(demodulated[i].startswith("aaaaaaaa"))
