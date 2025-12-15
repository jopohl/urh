import os
import sys
import unittest

from urh.ainterpretation import AutoInterpretation
from urh.signalprocessing.Signal import Signal
from tests.auto_interpretation.auto_interpretation_test_util import demodulate


class TestAutoInterpretationIntegration(unittest.TestCase):
    SIGNALPATH = "~/GIT/publications/ainterpretation/experiments/signals/"

    def get_path(self, signalname):
        if sys.platform == "win32":
            return None

        path = os.path.join(os.path.expanduser(self.SIGNALPATH), signalname)
        if os.path.exists(path):
            return path
        else:
            return None

    def test_action(self):
        path = self.get_path("action_FB_A_B_C_D.coco")
        if not path:
            return

        data = Signal(path, "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(bit_length, 400)
        self.assertLessEqual(bit_length, 600)

        print(
            "noise",
            noise,
            "center",
            center,
            "bit length",
            bit_length,
            "tolerance",
            tolerance,
        )
        demodulated = demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 19)
        for i in range(2):
            self.assertTrue(demodulated[i].startswith("8e8eeeeeee8"))

    def test_audi(self):
        path = self.get_path("audi_auf_sr5m.coco")
        if not path:
            return

        data = Signal(path, "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(bit_length, 2400)
        self.assertLessEqual(bit_length, 2500)
        self.assertGreaterEqual(center, 0.005)
        self.assertLessEqual(center, 0.32)

        print(
            "noise",
            noise,
            "center",
            center,
            "bit length",
            bit_length,
            "tolerance",
            tolerance,
        )
        demodulated = demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 1)
        self.assertTrue(
            demodulated[0].startswith(
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            )
        )
        self.assertTrue(demodulated[0].endswith("cad4c"))

    def test_brennenstuhl(self):
        path = self.get_path("brennenstuhl_signal_ABCD_onoff.coco")
        if not path:
            return

        data = Signal(path, "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "ASK")
        self.assertEqual(bit_length, 300)

        print(
            "noise",
            noise,
            "center",
            center,
            "bit length",
            bit_length,
            "tolerance",
            tolerance,
        )
        demodulated = demodulate(
            data, mod_type, bit_length, center, noise, tolerance, pause_threshold=8
        )
        print(demodulated)
        self.assertEqual(len(demodulated), 64)
        for i in range(64):
            self.assertTrue(demodulated[i].startswith("88888888888"))
            self.assertEqual(len(demodulated[i]), len(demodulated[0]))

    def test_esaver(self):
        path = self.get_path("esaver_test4on.complex")
        if not path:
            return

        data = Signal(path, "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        print(center, noise)
        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)

        print(
            "noise",
            noise,
            "center",
            center,
            "bit length",
            bit_length,
            "tolerance",
            tolerance,
        )
        demodulated = demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 12)
        for i in range(12):
            self.assertTrue(demodulated[i].startswith("aaaaaaaa"))

    def test_scislo(self):
        path = self.get_path("scislo.complex")
        if not path:
            return

        data = Signal(path, "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 200)
        self.assertGreaterEqual(noise, 0.0120)

        print(
            "noise",
            noise,
            "center",
            center,
            "bit length",
            bit_length,
            "tolerance",
            tolerance,
        )
        demodulated = demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 8)
        for i in range(8):
            self.assertTrue(demodulated[i].startswith("000000000000aaaaaa"))

    def test_vw(self):
        path = self.get_path("vw_auf.complex")
        if not path:
            return

        data = Signal(path, "").iq_array

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = (
            result["center"],
            result["noise"],
            result["tolerance"],
        )

        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(bit_length, 2000)
        self.assertLessEqual(bit_length, 3000)

        demodulated = demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 1)
        self.assertTrue(
            demodulated[0].startswith(
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            )
        )
