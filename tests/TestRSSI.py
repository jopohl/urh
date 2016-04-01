import os
import unittest

from PyQt5.QtTest import QTest

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestRSSI(unittest.TestCase):
    # Testmethode muss immer mit Präfix test_* starten
    def test_get_rssi_of_block(self):
        signal = Signal(os.path.realpath(os.path.join(os.curdir, "data", "two_participants.complex")), "RSSI-Test")
        QTest.qWait(10)
        signal.modulation_type = 1
        signal.bit_len = 100
        signal.qad_center = -0.0507

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.num_blocks, 18)
        blocks = proto_analyzer.blocks
        self.assertLess(blocks[0].rssi, blocks[1].rssi)
        self.assertGreater(blocks[1].rssi, blocks[2].rssi)
        self.assertLess(blocks[2].rssi, blocks[3].rssi)
        self.assertLess(blocks[-2].rssi, blocks[-1].rssi)