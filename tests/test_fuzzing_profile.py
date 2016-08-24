import unittest
import os
import tempfile

from urh import constants
from urh.cythonext.signalFunctions import Symbol
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.Message import Message
from urh.signalprocessing.encoding import encoding


class TestFuzzing(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(tempfile.gettempdir(), "test.fuzz")
        mod1 = Modulator("mod 1")
        mod2 = Modulator("mod 2")
        mod2.param_for_one = 42

        decoders = [encoding(["NRZ"]), encoding(["NRZ-I", constants.DECODING_INVERT])]

        pac = ProtocolAnalyzerContainer([mod1, mod2])
        pac.blocks.append(Message([True, False, False, True, "A"], 100, decoder=decoders[0], labelset=pac.default_labelset))
        pac.blocks.append(Message([False, False, False, False, "A"], 200, decoder=decoders[1], labelset=pac.default_labelset))
        pac.used_symbols.add(Symbol("A", 1, 1, 100))
        pac.create_fuzzing_label(1, 10, 0)
        pac.to_xml_file(filename)

    def test_load_profile(self):
        pac = ProtocolAnalyzerContainer([])
        pac.from_xml_file(os.path.join(tempfile.gettempdir(), "test.fuzz"))

        self.assertEqual(len(pac.used_symbols), 1)
        self.assertEqual(len(pac.modulators), 2)
        self.assertEqual(len(pac.blocks), 2)
        self.assertEqual(pac.blocks[1][0], False)
        self.assertEqual(len(pac.protocol_labels), 1)