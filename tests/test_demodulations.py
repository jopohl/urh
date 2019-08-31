import array
import unittest

import numpy as np

from tests.utils_testing import get_path_for_data_file
from urh.cythonext.signal_functions import modulate_c
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestDemodulations(unittest.TestCase):
    def test_ask(self):
        signal = Signal(get_path_for_data_file("ask.complex"), "ASK-Test")
        signal.modulation_type = "ASK"
        signal.bit_len = 295
        signal.qad_center = 0.0219
        self.assertEqual(signal.num_samples, 13710)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertTrue(proto_analyzer.plain_bits_str[0].startswith("1011001001011011011011011011011011001000000"))

    def test_ask_two(self):
        signal = Signal(get_path_for_data_file("ask_short.complex"), "ASK-Test2")
        signal.modulation_type = "ASK"
        signal.noise_threshold = 0.0299
        signal.bit_len = 16
        signal.qad_center = 0.1300
        signal.tolerance = 0
        self.assertEqual(signal.num_samples, 131)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.plain_bits_str[0], "10101010")

    def test_fsk(self):
        signal = Signal(get_path_for_data_file("fsk.complex"), "FSK-Test")
        signal.modulation_type = "FSK"
        signal.bit_len = 100
        signal.qad_center = 0

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.plain_bits_str[0],
                         "101010101010101010101010101010101100011000100110110001100010011011110100110111000001110110011000111011101111011110100100001001111001100110011100110100100011100111010011111100011")

    def test_fsk_short_bit_length(self):
        bits_str = "101010"
        bits = array.array("B", list(map(int, bits_str)))
        parameters = array.array("f", [-10e3, 10e3])
        result = modulate_c(bits, 8, "FSK", parameters, 1, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        signal = Signal("")
        signal.iq_array = IQArray(result)

        # Ensure we have no spikes
        self.assertLess(np.max(signal.qad), 1)

        signal.qad_center = 0
        signal.bit_len = 8

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.plain_bits_str[0], bits_str)

    def test_psk(self):
        signal = Signal(get_path_for_data_file("psk_gen_noisy.complex"), "PSK-Test")
        signal.modulation_type = "PSK"
        signal.bit_len = 300
        signal.qad_center = -1.2886
        signal.noise_threshold = 0
        signal.tolerance = 10

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertTrue(proto_analyzer.plain_bits_str[0].startswith("1011"), msg=proto_analyzer.plain_bits_str[0])

    def test_4_fsk(self):
        bits = array.array("B", [1, 0, 1, 0, 1, 1, 0, 0, 0, 1])
        parameters = array.array("f", [-20e3, -10e3, 10e3, 20e3])
        result = modulate_c(bits, 100, "FSK", parameters, 2, 1, 40e3, 0, 1e6, 1000, 0, parameters[0])

        signal = Signal("")
        signal.iq_array = IQArray(result)
        signal.bits_per_symbol = 2
        signal.qad_center = 0

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.plain_bits_str[0], "1010110001")

