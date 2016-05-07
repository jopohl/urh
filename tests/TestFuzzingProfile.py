import unittest
import os
import tempfile

from urh.cythonext.signalFunctions import Symbol
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.encoding import encoding


class TestFuzzing(unittest.TestCase):
    def test_save_profile(self):
        filename = os.path.join(tempfile.gettempdir(), "test.fuzz")
        mod1 = Modulator("mod 1")
        mod2 = Modulator("mod 2")
        mod2.param_for_one = 42

        decoders = [encoding(["NRZ"])]

        pac = ProtocolAnalyzerContainer([mod1, mod2], decoders)
        pac.blocks.append(ProtocolBlock([True, False, False, True, "A"], 100, [], decoder=decoders[0]))
        pac.used_symbols.add(Symbol("A", 1, 1, 100))
        pac.create_fuzzing_label(1, 10, 0)
        pac.to_xml_file(filename)

    def test_load_profile(self):
        pass