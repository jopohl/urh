import os
import tempfile
import unittest

from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestProtocolAnalyzer(unittest.TestCase):
    def test_get_bit_sample_pos(self):
        signal = Signal(
            get_path_for_data_file("ASK_mod.complex"), "Bit sample pos test"
        )
        signal.modulation_type = "ASK"
        signal.samples_per_symbol = 100

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.num_messages, 1)
        for i, pos in enumerate(proto_analyzer.messages[0].bit_sample_pos):
            self.assertLess(pos, signal.num_samples, msg=i)

    def test_fsk_freq_detection(self):
        s = Signal(get_path_for_data_file("steckdose_anlernen.complex"), "RWE")
        s.noise_threshold = 0.06
        s.center = 0
        s.samples_per_symbol = 100
        pa = ProtocolAnalyzer(s)
        pa.get_protocol_from_signal()
        self.assertEqual(
            pa.messages[0].plain_bits_str,
            "101010101010101010101010101010101001101001111101100110100111110111010010011000010110110101111"
            "010111011011000011000101000010001001101100101111010110100110011100100110000101001110100001111"
            "111101000111001110000101110100100111010110110100001101101101010100011011010001010110011100011"
            "010100010101111110011010011001000000110010011010001000100100100111101110110010011111011100010"
            "10110010100011111101110111000010111100111101001011101101011011010110101011100",
        )

        freq = pa.estimate_frequency_for_one(1e6)
        self.assertEqual(1, int(freq / 10000))  # Freq for 1 is 10K
        freq = pa.estimate_frequency_for_zero(1e6)
        self.assertEqual(3, int(freq / 10000))  # Freq for 0 is 30K

    def test_get_rssi_of_message(self):
        signal = Signal(
            get_path_for_data_file("two_participants.complex16s"), "RSSI-Test"
        )
        signal.modulation_type = "FSK"
        signal.samples_per_symbol = 100
        signal.center = -0.0507

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.num_messages, 18)
        messages = proto_analyzer.messages
        self.assertLess(messages[0].rssi, messages[1].rssi)
        self.assertGreater(messages[1].rssi, messages[2].rssi)
        self.assertLess(messages[2].rssi, messages[3].rssi)
        self.assertLess(messages[-2].rssi, messages[-1].rssi)

    def test_binary_format(self):
        pa = ProtocolAnalyzer(None)
        pa.messages.append(
            Message(
                [1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1],
                0,
                pa.default_message_type,
            )
        )
        pa.messages.append(Message([1, 1, 1, 0, 1], 0, pa.default_message_type))

        filename = os.path.join(tempfile.gettempdir(), "test_proto.bin")
        pa.to_binary(filename, use_decoded=True)

        pa.from_binary(filename)
        self.assertEqual(len(pa.messages), 3)
        self.assertEqual(pa.plain_bits_str[2], "111000111001101111101000")
