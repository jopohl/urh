import unittest

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.Ruleset import DataRule, Ruleset, Mode


class TestLabels(unittest.TestCase):
    def setUp(self):
        self.protocol = ProtocolAnalyzer(None)
        with open("./data/rwe_decoded_bits.txt") as f:
            for line in f:
                self.protocol.blocks.append(ProtocolBlock.from_plain_bits_str(line.replace("\n", ""), {}))
                self.protocol.blocks[-1].labelset = self.protocol.default_labelset

        self.assertEqual(self.protocol.num_blocks, 42)
        self.assertEqual(self.protocol.plain_hex_str[0][16:18], "2d")

    def test_assign_by_value(self):
        start = 8
        end = 15
        hex_value = "9a7d9a7d"

        lblset = LabelSet("autotest")
        lblset.ruleset = Ruleset(Mode.all_apply, [DataRule(start, end, "=", hex_value, 1)])
        lblset.assigned_automatically = True

        self.protocol.labelsets.append(lblset)
        self.protocol.update_auto_labelsets()
        matching_indices = [0, 2, 3, 21, 23, 24]
        for i, block in enumerate(self.protocol.blocks):
            if i in matching_indices:
                self.assertEqual(block.labelset, lblset, msg=str(i))
            else:
                self.assertEqual(block.labelset, self.protocol.default_labelset, msg=str(i))