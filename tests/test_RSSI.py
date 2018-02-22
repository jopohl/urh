import unittest

from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestRSSI(unittest.TestCase):
    def test_get_rssi_of_message(self):
        signal = Signal(get_path_for_data_file("two_participants.complex"), "RSSI-Test")
        signal.modulation_type = 1
        signal.bit_len = 100
        signal.qad_center = -0.0507

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.num_messages, 18)
        messages = proto_analyzer.messages
        self.assertLess(messages[0].rssi, messages[1].rssi)
        self.assertGreater(messages[1].rssi, messages[2].rssi)
        self.assertLess(messages[2].rssi, messages[3].rssi)
        self.assertLess(messages[-2].rssi, messages[-1].rssi)
