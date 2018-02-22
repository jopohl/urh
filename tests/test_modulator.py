import array
import os
import time
import unittest

from PyQt5.QtCore import QDir

from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestModulator(unittest.TestCase):
    def setUp(self):
        self.modulation_data = array.array("B", [True, False, False, False, True, True, False, True])
        self.samples_per_bit = 100
        self.pause = 1000

        self.total_samples = len(self.modulation_data) * self.samples_per_bit + self.pause

    def test_ask_fsk_psk_modulation(self):
        modulations = ["ASK", "FSK", "PSK"]

        for i, modulation in enumerate(modulations):
            modulator = Modulator(modulation)
            tmp_dir = QDir.tempPath()
            filename = "{0}_mod.complex".format(modulation)
            filename = os.path.join(tmp_dir, filename)
            modulator.modulation_type = i
            modulator.samples_per_bit = self.samples_per_bit

            if modulation == "ASK":
                modulator.param_for_zero = 0
                modulator.param_for_one = 100
            elif modulation == "FSK":
                modulator.param_for_zero = 1000
                modulator.param_for_one = 2500
            elif modulation == "PSK":
                modulator.param_for_zero = 0
                modulator.param_for_one = 180

            modulator.modulate(self.modulation_data, self.pause).tofile(filename)

            signal = Signal(filename, modulation)
            signal.modulation_type = i
            signal.bit_len = self.samples_per_bit
            if modulation == "ASK":
                signal.qad_center = 0.5
            elif modulation == "FSK":
                signal.qad_center = 0.0097
            elif modulation == "PSK":
                signal.qad_center = 0
            self.assertEqual(signal.num_samples, self.total_samples, msg=modulation)
            pa = ProtocolAnalyzer(signal)
            pa.get_protocol_from_signal()
            self.assertEqual(1, len(pa.messages), msg=modulation)
            self.assertEqual(self.modulation_data, pa.messages[0].plain_bits, msg=modulation)

    def test_performance(self):
        t = time.time()
        modulator = Modulator("Perf")
        modulator.modulation_type = 1
        modulator.modulate([True] * 1000, pause=10000000)
        elapsed = time.time() - t
        self.assertLess(elapsed, 0.5)
