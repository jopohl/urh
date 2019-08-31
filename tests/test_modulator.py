import array
import os
import tempfile
import time
import unittest

import numpy as np
from PyQt5.QtCore import QDir

from urh.cythonext.signal_functions import modulate_c
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestModulator(unittest.TestCase):
    def setUp(self):
        self.modulation_data = array.array("B", [True, False, False, False, True, True, False, True])
        self.samples_per_symbol = 100
        self.pause = 1000

        self.total_samples = len(self.modulation_data) * self.samples_per_symbol + self.pause

    def test_ask_fsk_psk_modulation(self):
        modulations = ["ASK", "FSK", "PSK"]

        for modulation in modulations:
            modulator = Modulator(modulation)
            tmp_dir = QDir.tempPath()
            filename = "{0}_mod.complex".format(modulation)
            filename = os.path.join(tmp_dir, filename)
            modulator.modulation_type = modulation
            modulator.samples_per_symbol = self.samples_per_symbol

            if modulation == "ASK":
                modulator.param_for_zero = 0
                modulator.param_for_one = 100
            elif modulation == "FSK":
                modulator.param_for_zero = 1000
                modulator.param_for_one = 2500
            elif modulation == "PSK":
                modulator.param_for_zero = -90
                modulator.param_for_one = 90

            modulator.modulate(self.modulation_data, self.pause).tofile(filename)

            signal = Signal(filename, modulation)
            signal.modulation_type = modulation
            signal.bit_len = self.samples_per_symbol
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

    def test_gfsk(self):
        target_file = os.path.join(tempfile.gettempdir(), "test.complex")

        modulator = Modulator("gfsk")
        modulator.modulation_type = "GFSK"
        modulator.samples_per_symbol = 100
        modulator.sample_rate = 1e6
        modulator.param_for_one = 20e3
        modulator.param_for_zero = -10e3
        data1 = modulator.modulate([True, False, False, True, False], 9437)
        data2 = modulator.modulate([True, False, True], 9845) #, start=len(s))
        data3 = modulator.modulate([True, False, True, False], 8458) #, start=len(s))
        s = np.concatenate((data1, data2, data3))

        s.tofile(target_file)

        pa = ProtocolAnalyzer(Signal(target_file, "test", modulation="FSK"))
        pa.get_protocol_from_signal()

    def test_performance(self):
        t = time.time()
        modulator = Modulator("Perf")
        modulator.modulation_type = "FSK"
        modulator.modulate([True] * 1000, pause=10000000)
        elapsed = time.time() - t
        self.assertLess(elapsed, 0.5)

    def test_c_modulation_method_ask(self):
        bits = array.array("B", [1, 0, 1, 0, 1, 1, 0, 0, 0, 1])
        parameters = array.array("f", [0, 0.25, 0.5, 1])
        result = modulate_c(bits, 100, "ASK", parameters, 2, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        #result.tofile("/tmp/test.complex")

    def test_c_modulation_method_fsk(self):
        bits = array.array("B", [1, 0, 1, 0, 1, 1, 0, 0, 0, 1])
        parameters = array.array("f", [-10e3, 10e3])
        result = modulate_c(bits, 100, "FSK", parameters, 1, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        #result.tofile("/tmp/test_fsk.complex")

    def test_c_modulation_method_psk(self):
        bits = array.array("B", [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1])
        parameters = array.array("f", [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4])
        result = modulate_c(bits, 100, "PSK", parameters, 2, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        # result.tofile("/tmp/test_psk.complex")

    def test_c_modulation_method_oqpsk(self):
        bits = array.array("B", [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1])
        parameters = array.array("f", [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4])
        result = modulate_c(bits, 100, "OQPSK", parameters, 2, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        # result.tofile("/tmp/test_oqpsk.complex")

    def test_c_modulation_method_gfsk(self):
        bits = array.array("B", [1, 0, 1, 0, 1, 1, 0, 0, 0, 1])
        parameters = array.array("f", [-10e3, 10e3])
        result = modulate_c(bits, 100, "GFSK", parameters, 1, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        # result.tofile("/tmp/test_gfsk.complex")
