import os
import tempfile

from tests.QtTestCase import QtTestCase
from urh import constants
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.Symbol import Symbol
from urh.signalprocessing.encoder import Encoder


class TestFuzzing(QtTestCase):
    def setUp(self):
        filename = os.path.join(tempfile.gettempdir(), "test.fuzz")
        mod1 = Modulator("mod 1")
        mod2 = Modulator("mod 2")
        mod2.param_for_one = 42

        decoders = [Encoder(["NRZ"]), Encoder(["NRZ-I", constants.DECODING_INVERT])]

        pac = ProtocolAnalyzerContainer([mod1, mod2])
        pac.messages.append(Message([True, False, False, True, "A"], 100, decoder=decoders[0], message_type=pac.default_message_type))
        pac.messages.append(Message([False, False, False, False, "A"], 200, decoder=decoders[1], message_type=pac.default_message_type))
        pac.used_symbols.add(Symbol("A", 1, 1, 100))
        pac.create_fuzzing_label(1, 10, 0)
        pac.to_xml_file(filename)

    def test_load_profile(self):
        pac = ProtocolAnalyzerContainer([])
        pac.from_xml_file(os.path.join(tempfile.gettempdir(), "test.fuzz"))

        self.assertEqual(len(pac.used_symbols), 1)
        self.assertEqual(len(pac.modulators), 2)
        self.assertEqual(len(pac.messages), 2)
        self.assertEqual(pac.messages[1][0], False)
        self.assertEqual(len(pac.protocol_labels), 1)
