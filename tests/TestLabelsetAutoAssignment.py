import unittest

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock


class TestLabels(unittest.TestCase):
    def setUp(self):
        self.protocol = ProtocolAnalyzer(None)
        with open("./data/rwe_decoded_bits.txt") as f:
            for line in f:
                self.protocol.blocks.append(ProtocolBlock.from_plain_bits_str(line.replace("\n", ""), {}))

        self.assertEqual(self.protocol.num_blocks, 42)
        self.assertEqual(self.protocol.plain_hex_str[0][16:18], "2d")

    def test_assign_by_value(self):
        print("\n".join(self.protocol.plain_hex_str))