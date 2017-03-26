import copy
import sys
import unittest

import sip
from PyQt5.QtWidgets import QApplication

from tests import utils_testing
from tests.utils_testing import get_path_for_data_file
from urh.dev.PCAP import PCAP
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal

utils_testing.write_settings()



class TestPCAP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)

    def test_write(self):
        signal = Signal(get_path_for_data_file("ask.complex"), "ASK-Test")
        signal.modulation_type = 0
        signal.bit_len = 295
        signal.qad_center = -0.1667
        self.assertEqual(signal.num_samples, 13710)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.decoded_hex_str[0], "b25b6db6c80")

        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))


        pcap = PCAP()
        pcap.write_packets(proto_analyzer.messages, "/tmp/test.pcap", 1e6)
