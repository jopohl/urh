import unittest

from PyQt5.QtTest import QTest

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestDemodulations(unittest.TestCase):

    # Testmethode muss immer mit Präfix test_* starten
    def test_ask(self):
        signal = Signal("./data/ask.complex", "ASK-Test")
        QTest.qWait(100)
        signal.modulation_type = 0
        signal.bit_len = 295
        signal.qad_center = -0.1667
        self.assertEqual(signal.num_samples, 13710)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertTrue(proto_analyzer.plain_bits_str[0].startswith("1011001001011011011011011011011011001000000"))

    def test_fsk(self):
        signal = Signal("./data/fsk.complex", "FSK-Test")
        QTest.qWait(100)
        signal.modulation_type = 1
        signal.bit_len = 100
        signal.qad_center = 0

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.plain_bits_str[0],
                         "101010101010101010101010101010101100011000100110110001100010011011110100110111000001110110011000111011101111011110100100001001111001100110011100110100100011100111010011111100011")

    def test_psk(self):
        signal = Signal("./data/psk_gen_noisy.complex", "PSK-Test")
        QTest.qWait(100)
        signal.modulation_type = 2
        signal.bit_len = 300
        signal.qad_center = 0.0281
        signal.noise_treshold = 0
        signal.tolerance = 10

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.plain_bits_str[0], "101100")
