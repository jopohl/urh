import unittest

from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal

class TestSignal(unittest.TestCase):
    def test_freq_detection(self):
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

        start, nsamples = pa.get_samplepos_of_bitseq(0, 0, 0, 1, False)
        freq = s.estimate_frequency(start, start + nsamples, 1e6)
        self.assertEqual(freq, 10000)  # Freq for 1 is 10K
