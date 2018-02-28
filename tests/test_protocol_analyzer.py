import unittest

from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestProtocolAnalyzer(unittest.TestCase):
    def test_get_bit_sample_pos(self):
        signal = Signal(get_path_for_data_file("ASK_mod.complex"), "Bit sample pos test")
        signal.modulation_type = 0
        signal.bit_len = 100

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.num_messages, 1)
        for i, pos in enumerate(proto_analyzer.messages[0].bit_sample_pos):
            self.assertLess(pos, signal.num_samples, msg=i)

    def test_fsk_freq_detection(self):
        s = Signal(get_path_for_data_file("steckdose_anlernen.complex"), "RWE")
        s.noise_threshold = 0.06
        s.qad_center = 0
        s.bit_len = 100
        pa = ProtocolAnalyzer(s)
        pa.get_protocol_from_signal()
        self.assertEqual(pa.messages[0].plain_bits_str,
                         "101010101010101010101010101010101001101001111101100110100111110111010010011000010110110101111"
                         "010111011011000011000101000010001001101100101111010110100110011100100110000101001110100001111"
                         "111101000111001110000101110100100111010110110100001101101101010100011011010001010110011100011"
                         "010100010101111110011010011001000000110010011010001000100100100111101110110010011111011100010"
                         "10110010100011111101110111000010111100111101001011101101011011010110101011100")

        freq = pa.estimate_frequency_for_one(1e6)
        self.assertEqual(1, int(freq / 10000))  # Freq for 1 is 10K
        freq = pa.estimate_frequency_for_zero(1e6)
        self.assertEqual(3, int(freq / 10000))  # Freq for 0 is 30K
