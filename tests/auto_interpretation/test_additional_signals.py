import os
import unittest

import numpy as np

from urh.ainterpretation import AutoInterpretation
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestAutoInterpretationIntegration(unittest.TestCase):
    SIGNALPATH = "~/GIT/publications/ainterpretation/experiments/signals/"

    def get_path(self, signalname):
        path = os.path.join(os.path.expanduser(self.SIGNALPATH), signalname)
        if os.path.exists(path):
            return path
        else:
            return None


    def demodulate(self, signal_data, mod_type: str, bit_length, center, noise, tolerance, decoding=None,
                   pause_threshold=None):
        signal = Signal("", "")
        signal._fulldata = signal_data
        signal.modulation_type = signal.MODULATION_TYPES.index(mod_type)
        signal.bit_len = bit_length
        signal.qad_center = center
        signal.noise_threshold = noise
        if pause_threshold is not None:
            signal.pause_threshold = pause_threshold
        if tolerance is not None:
            signal.tolerance = tolerance
        pa = ProtocolAnalyzer(signal)
        if decoding is not None:
            pa.decoder = decoding
        pa.get_protocol_from_signal()
        return pa.decoded_hex_str

    def test_action(self):
        path = self.get_path("action_FB_A_B_C_D.coco")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(bit_length, 400)
        self.assertLessEqual(bit_length, 500)

        print("noise", noise, "center", center, "bit length", bit_length, "tolerance", tolerance)
        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 19)
        for i in range(2):
            self.assertTrue(demodulated[i].startswith("8e8eeeeeee8"))

    def test_audi(self):
        path = self.get_path("audi_auf_sr5m.coco")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(bit_length, 2400)
        self.assertLessEqual(bit_length, 2500)
        self.assertGreaterEqual(center, 0.005)
        self.assertLessEqual(center, 0.1265)

        print("noise", noise, "center", center, "bit length", bit_length, "tolerance", tolerance)
        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 2)
        for i in range(2):
            self.assertTrue(demodulated[i].startswith("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"))
            self.assertTrue(demodulated[i].endswith("cad4c"))
            self.assertEqual(len(demodulated[0]), len(demodulated[i]))

    def test_brennenstuhl(self):
        path = self.get_path("brennenstuhl_signal_ABCD_onoff.coco")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "ASK")
        self.assertEqual(bit_length, 300)

        print("noise", noise, "center", center, "bit length", bit_length, "tolerance", tolerance)
        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance, pause_threshold=8)
        print(demodulated)
        self.assertEqual(len(demodulated), 64)
        for i in range(64):
            self.assertTrue(demodulated[i].startswith("88888888888"))
            self.assertEqual(len(demodulated[i]), len(demodulated[0]))

    def test_homematic(self):
        path = self.get_path("homematic_kommunikation_an0.complex")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)

        print(center, noise, tolerance)
        print(center, noise, tolerance, bit_length)
        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 4)
        for i in range(4):
            self.assertTrue(demodulated[i].startswith("aaaaaaaa"))

    def test_esaver(self):
        path = self.get_path("esaver_test4on.complex")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        print(center, noise)
        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 100)

        print("noise", noise, "center", center, "bit length", bit_length, "tolerance", tolerance)
        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 21)
        for i in range(8):
            self.assertTrue(demodulated[i].startswith("aaaaaaaa"))

    def test_scislo(self):
        path = self.get_path("scislo.complex")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "FSK")
        self.assertEqual(bit_length, 200)
        self.assertGreaterEqual(noise, 0.0120)

        print("noise", noise, "center", center, "bit length", bit_length, "tolerance", tolerance)
        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 8)
        for i in range(8):
            self.assertTrue(demodulated[i].startswith("000000000000aaaaaa"))

    def test_vw(self):
        path = self.get_path("vw_auf.complex")
        if not path:
            return

        data = Signal(path, "").data

        result = AutoInterpretation.estimate(data)
        mod_type, bit_length = result["modulation_type"], result["bit_length"]
        center, noise, tolerance = result["center"], result["noise"], result["tolerance"]

        self.assertEqual(mod_type, "ASK")
        self.assertGreaterEqual(bit_length, 2000)
        self.assertLessEqual(bit_length, 3000)

        demodulated = self.demodulate(data, mod_type, bit_length, center, noise, tolerance)
        print(demodulated)
        self.assertEqual(len(demodulated), 1)
        self.assertTrue(demodulated[0].startswith("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"))