import os
import unittest

from PyQt5.QtTest import QTest

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestRSSI(unittest.TestCase):
    # Testmethode muss immer mit Präfix test_* starten
    def test_get_rssi_of_message(self):
        signal = Signal(os.path.realpath(os.path.join(os.curdir, "data", "two_participants.complex")), "RSSI-Test")
        QTest.qWait(10)
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