import copy
import unittest

import time

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Ruleset import Rule, Ruleset, Mode
from urh.signalprocessing.encoding import encoding


class TestAutoAssignments(unittest.TestCase):
    def setUp(self):
        self.protocol = ProtocolAnalyzer(None)
        with open("./data/decoded_bits.txt") as f:
            for line in f:
                self.protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", ""), {}))
                self.protocol.messages[-1].labelset = self.protocol.default_labelset

        # Assign participants
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        alice_indices = {1,2,5,6,9,10,13,14,17,18,20,22,23,26,27,30,31,34,35,38,39,41}
        for i, message in enumerate(self.protocol.messages):
            if i in alice_indices:
                message.participant = alice
            else:
                message.participant = bob

        self.assertEqual(self.protocol.num_messages, 42)
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
        for i, message in enumerate(self.protocol.messages):
            if i in matching_indices:
                self.assertEqual(message.labelset, lblset, msg=str(i))
            else:
                self.assertEqual(message.labelset, self.protocol.default_labelset, msg=str(i))

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
            message = copy.deepcopy(self.protocol.messages[i])
            message.participant = None
            proto1.messages.append(message)
            proto1.messages[i].rssi = rssis[0][i]

        self.assertEqual(len(proto1.messages), 21)


        for i in range(0, len(rssis[1])):
            message = copy.deepcopy(self.protocol.messages[21 + i])
            message.participant = None
            proto2.messages.append(message)
            proto2.messages[i].rssi = rssis[1][i]

        self.assertEqual(len(proto2.messages), 21)

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
        for i, message in enumerate(proto1.messages):
            self.assertEqual(message.participant, excpected_partis[0][i])

        proto2.auto_assign_participants([alice, bob])
        for i, message in enumerate(proto2.messages):
            self.assertEqual(message.participant, excpected_partis[1][i])

    def test_assign_decodings(self):
        self.undecoded_protocol = ProtocolAnalyzer(None)
        with open("./data/undecoded.txt") as f:
            for line in f:
                self.undecoded_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", ""), {}))

        self.undecoded_protocol.auto_assign_decodings(self.decodings)

        for i, message in enumerate(self.undecoded_protocol.messages):
            if message.plain_hex_str[8:16] == "9a7d9a7d":
                self.assertEqual(message.decoder.name, "DeWhitening Special", msg=str(i))
            elif message.plain_hex_str[8:16] == "67686768":
                self.assertEqual(message.decoder.name, "DeWhitening", msg=str(i))


    def test_assign_labels_trash_protocol(self):
        preamble_start = 0
        preamble_end = 31
        sync_start = 32
        sync_end = 63

        decoded_trash_protocol = ProtocolAnalyzer(None)
        with open("./data/decoded_with_trash.txt") as f:
            for line in f:
                decoded_trash_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", ""), {}))
                decoded_trash_protocol.messages[-1].labelset = decoded_trash_protocol.default_labelset

        decoded_trash_protocol.auto_assign_labels()

        preamble_label = ProtocolLabel(name="Preamble", start=preamble_start, end=preamble_end, val_type_index=0, color_index=0)
        sync_label = ProtocolLabel(name="Sync", start=sync_start, end=sync_end, val_type_index=0, color_index=1)

        self.assertEqual(1, len([lbl for lbl in decoded_trash_protocol.default_labelset if lbl.name == "Preamble"]))
        self.assertEqual(1, len([lbl for lbl in decoded_trash_protocol.default_labelset if lbl.name == "Sync"]))

        for message in decoded_trash_protocol.messages:
            self.assertIn(preamble_label, message.labelset)
            self.assertIn(sync_label, message.labelset)

    def test_assign_labels(self):
        preamble_start = 0
        preamble_end = 31
        sync_start = 32
        sync_end = 63
        length_start = 64
        length_end = 71

        t = time.time()
        self.protocol.auto_assign_labels(debug=True)
        print("Time for auto assigning labels: ", str(time.time()-t)) # 0.020628690719604492

        preamble_label = ProtocolLabel(name="Preamble", start=preamble_start, end=preamble_end, val_type_index=0, color_index=0)
        sync_label = ProtocolLabel(name="Sync", start=sync_start, end=sync_end, val_type_index=0, color_index=1)
        length_label = ProtocolLabel(name="Length", start=length_start, end=length_end, val_type_index=0, color_index=2)

        self.assertEqual(1, len([lbl for lbl in self.protocol.default_labelset if lbl.name == "Preamble"]))
        self.assertEqual(1, len([lbl for lbl in self.protocol.default_labelset if lbl.name == "Sync"]))
        self.assertEqual(1, len([lbl for lbl in self.protocol.default_labelset if lbl.name == "Length"]))

        for message in self.protocol.messages:
            self.assertIn(preamble_label, message.labelset)
            self.assertIn(sync_label, message.labelset)
            self.assertIn(length_label, message.labelset)


    def test_assign_constants(self):
        const_start = 82
        const_end = 104
        const = "1110001011110101010111"

        const_protocol = ProtocolAnalyzer(None)
        with open("./data/constant_bits.txt") as f:
            for line in f:
                const_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", ""), {}))
                self.assertEqual(const_protocol.messages[-1].decoded_bits_str, line.replace("\n", ""))
                const_protocol.messages[-1].labelset = const_protocol.default_labelset

        for message in const_protocol.messages:
            assert message.decoded_bits_str[const_start:const_end] == const

        const_protocol.auto_assign_labels()
        const_label = ProtocolLabel(name="Constant #1", start=const_start, end=const_end, val_type_index=0, color_index=0)
        self.assertEqual(1, len([lbl for lbl in const_protocol.default_labelset if lbl.name == const_label.name]))

        for message in const_protocol.messages:
            self.assertIn(const_label, message.labelset)