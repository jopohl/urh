import os
import unittest
from urh import constants

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.encoding import encoding


class TestLoadProtocolFile(unittest.TestCase):
    # Testmethode muss immer mit Präfix test_* starten
    def test_proto_block_from_str(self):
        bits = "1011AB11"
        pb = ProtocolBlock.from_plain_bits_str(bits)
        self.assertEqual(bits, pb.plain_bits_str)

    # def test_proto_analyzer_from_file(self):
    #     # TODO Compareframe methode nutzen, auch testen ob Labels da sind
    #     self.assertTrue(os.path.isfile("./data/protocol.txt"))
    #     pa, view_type, encoding = ProtocolAnalyzer.from_file("./data/protocol.txt")
    #     self.assertEqual(pa.blocks[0].plain_bits_str,
    #                      "10101010110100111011010111011101110111011100110001011101010001011101110110110101101")


if __name__ == "__main__":
    unittest.main()