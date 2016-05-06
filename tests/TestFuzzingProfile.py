import unittest
import os
import tempfile

from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.encoding import encoding


class TestFuzzing(unittest.TestCase):
    def test_save_profile(self):
        filename = os.path.join(tempfile.gettempdir(), "test.fuzz")
        mod1 = Modulator("mod 1")
        mod2 = Modulator("mod 2")
        mod2.param_for_one = 42

        decoders = [encoding(["NRZ"])]

        pac = ProtocolAnalyzerContainer([mod1, mod2], decoders)
        pac.to_xml_file(filename)