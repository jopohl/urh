import unittest

from urh.cli import urh_cli
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestCLILogic(unittest.TestCase):
    def test_cli_modulate_messages(self):
        modulator = Modulator("test")
        modulator.sample_rate = 2e3
        modulator.samples_per_symbol = 100
        modulator.modulation_type = "ASK"
        modulator.parameters[0] = 0
        modulator.parameters[1] = 100

        bits = "1010111100001"

        self.assertIsNone(urh_cli.modulate_messages([], modulator))

        message = Message.from_plain_bits_str(bits, pause=1000)

        modulated = urh_cli.modulate_messages([message], modulator)

        # Demodulate for testing
        s = Signal("", "", modulation="ASK", sample_rate=2e6)
        s.samples_per_symbol = 100
        s.noise_threshold = 0
        s.iq_array = modulated

        pa = ProtocolAnalyzer(s)
        pa.get_protocol_from_signal()
        self.assertEqual(len(pa.messages), 1)
        self.assertEqual(pa.messages[0].plain_bits_str, bits)
