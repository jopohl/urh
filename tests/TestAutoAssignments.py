import unittest

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.Ruleset import Rule, Ruleset, Mode
from urh.signalprocessing.encoding import encoding


class TestAutoAssignments(unittest.TestCase):
    def setUp(self):
        self.protocol = ProtocolAnalyzer(None)
        with open("./data/rwe_decoded_bits.txt") as f:
            for line in f:
                self.protocol.blocks.append(ProtocolBlock.from_plain_bits_str(line.replace("\n", ""), {}))
                self.protocol.blocks[-1].labelset = self.protocol.default_labelset

        self.assertEqual(self.protocol.num_blocks, 42)
        self.assertEqual(self.protocol.plain_hex_str[0][16:18], "2d")

        self.decodings = []
        self.decodings.append(encoding(['Non Return To Zero (NRZ)']))
        self.decodings.append(encoding(['Non Return To Zero Inverted (NRZ-I)', 'Invert']))
        self.decodings.append(encoding(['Manchester I', 'Edge Trigger']))
        self.decodings.append(encoding(['Manchester II', 'Edge Trigger', 'Invert']))
        self.decodings.append(encoding(['Differential Manchester', 'Edge Trigger', 'Differential Encoding',]))
        self.decodings.append(encoding(['DeWhitening Special', 'Remove Data Whitening (CC1101)', '0x9a7d9a7d;0x21;0x8']))
        self.decodings.append(encoding(['DeWhitening', 'Remove Data Whitening (CC1101)', '0x67686768;0x21;0x8']))

    def test_labelset_assign_by_value(self):
        start = 8
        end = 15
        hex_value = "9a7d9a7d"

        lblset = LabelSet("autotest")
        lblset.ruleset = Ruleset(Mode.all_apply, [Rule(start, end, "=", hex_value, 1)])
        lblset.assigned_automatically = True

        self.protocol.labelsets.append(lblset)
        self.protocol.update_auto_labelsets()
        matching_indices = [0, 2, 3, 21, 23, 24]
        for i, block in enumerate(self.protocol.blocks):
            if i in matching_indices:
                self.assertEqual(block.labelset, lblset, msg=str(i))
            else:
                self.assertEqual(block.labelset, self.protocol.default_labelset, msg=str(i))

    def test_two_assign_participants_by_rssi(self):
        rssis = [[0.65389872, 0.13733707, 0.1226876, 0.73320961, 0.64940965, 0.12463234, 0.12296994,
                 0.68053716, 0.66020358, 0.12428901, 0.12312815, 0.69160986, 0.65582329, 0.12536003,
                 0.12587067, 0.66315573, 0.66313261, 0.12816505, 0.13491708, 0.66950738, 0.14047238],
                 [0.26651502, 0.2073856, 0.13547869, 0.25948182, 0.28204739, 0.13716124, 0.13526952,
                 0.24828221, 0.25431305, 0.13681877, 0.13650328, 0.28083691, 0.25550124, 0.13498682,
                 0.13611424, 0.2629154, 0.26388499, 0.13780586, 0.13561584, 0.27228078, 0.1356563]]

        proto1 = ProtocolAnalyzer(None)
        proto2 = ProtocolAnalyzer(None)

        for i in range(0, len(rssis[0])):
            proto1.blocks.append(self.protocol.blocks[i])
            proto1.blocks[i].rssi = rssis[0][i]

        self.assertEqual(len(proto1.blocks), 21)


        for i in range(0, len(rssis[1])):
            proto2.blocks.append(self.protocol.blocks[21+i])
            proto2.blocks[i].rssi = rssis[1][i]

        self.assertEqual(len(proto2.blocks), 21)

        alice = Participant(name="Alice", shortname="A")
        alice.relative_rssi = 1
        bob = Participant(name="Bob", shortname="B")
        bob.relative_rssi = 0
        excpected_partis = [[alice, bob, bob, alice, alice, bob, bob,
                  alice, alice, bob, bob, alice, alice, bob,
                  bob, alice, alice, bob, bob, alice, bob],
                  [alice, bob, bob, alice, alice, bob, bob,
                   alice, alice, bob, bob, alice, alice, bob,
                   bob, alice, alice, bob, bob, alice, bob]]

        proto1.auto_assign_participants([alice, bob])
        for i, block in enumerate(proto1.blocks):
            self.assertEqual(block.participant, excpected_partis[0][i])

        proto2.auto_assign_participants([alice, bob])
        for i, block in enumerate(proto2.blocks):
            self.assertEqual(block.participant, excpected_partis[1][i])

    def test_assign_decodings(self):
        self.undecoded_protocol = ProtocolAnalyzer(None)
        with open("./data/rwe_undecoded.txt") as f:
            for line in f:
                self.undecoded_protocol.blocks.append(ProtocolBlock.from_plain_bits_str(line.replace("\n", ""), {}))

        self.undecoded_protocol.auto_assign_decodings(self.decodings)

        for i, block in enumerate(self.undecoded_protocol.blocks):
            if block.plain_hex_str[8:16] == "9a7d9a7d":
                self.assertEqual(block.decoder.name, "DeWhitening Special", msg=str(i))
            elif block.plain_hex_str[8:16] == "67686768":
                self.assertEqual(block.decoder.name, "DeWhitening", msg=str(i))

    def test_assign_labels(self):
        preamble_start = 0
        preamble_end = 31
        sync_start = 32
        sync_end = 63

        self.protocol.auto_assign_labels()

        preamble_label = ProtocolLabel(name="Preamble", start=preamble_start, end=preamble_end, val_type_index=0, color_index=0)
        sync_label = ProtocolLabel(name="Sync", start=sync_start, end=sync_end, val_type_index=0, color_index=1)

        print(self.protocol.default_labelset)

        self.assertEqual(1, len([lbl for lbl in self.protocol.default_labelset if lbl.name == "Preamble"]))
        self.assertEqual(1, len([lbl for lbl in self.protocol.default_labelset if lbl.name == "Sync"]))

        print(self.protocol.default_labelset)

        for block in self.protocol.blocks:
            self.assertIn(preamble_label, block.labelset)
            self.assertIn(sync_label, block.labelset)