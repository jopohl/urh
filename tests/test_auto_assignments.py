import copy
import unittest

from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Ruleset import Rule, Ruleset, Mode


class TestAutoAssignments(unittest.TestCase):
    def setUp(self):
        self.protocol = ProtocolAnalyzer(None)
        with open(get_path_for_data_file("decoded_bits.txt")) as f:
            for line in f:
                self.protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))
                self.protocol.messages[-1].message_type = self.protocol.default_message_type

        # Assign participants
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        alice_indices = {1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 20, 22, 23, 26, 27, 30, 31, 34, 35, 38, 39, 41}
        for i, message in enumerate(self.protocol.messages):
            if i in alice_indices:
                message.participant = alice
            else:
                message.participant = bob

        self.assertEqual(self.protocol.num_messages, 42)
        self.assertEqual(self.protocol.plain_hex_str[0][16:18], "2d")

        self.decodings = []
        self.decodings.append(Encoding(['Non Return To Zero (NRZ)']))
        self.decodings.append(Encoding(['Non Return To Zero Inverted (NRZ-I)', 'Invert']))
        self.decodings.append(Encoding(['Manchester I', 'Edge Trigger']))
        self.decodings.append(Encoding(['Manchester II', 'Edge Trigger', 'Invert']))
        self.decodings.append(Encoding(['Differential Manchester', 'Edge Trigger', 'Differential Encoding', ]))
        self.decodings.append(Encoding(['DeWhitening Special', constants.DECODING_DATAWHITENING, '0x9a7d9a7d;0x21;0']))
        self.decodings.append(Encoding(['DeWhitening', constants.DECODING_DATAWHITENING, '0x67686768;0x21;0']))

    def test_message_type_assign_by_value(self):
        start = 8
        end = 15
        hex_value = "9a7d9a7d"

        msg_type = MessageType("autotest")
        msg_type.ruleset = Ruleset(Mode.all_apply, [Rule(start, end, "=", hex_value, 1)])
        msg_type.assigned_by_ruleset = True

        self.protocol.message_types.append(msg_type)
        self.protocol.update_auto_message_types()
        matching_indices = [0, 2, 3, 21, 23, 24]
        for i, message in enumerate(self.protocol.messages):
            if i in matching_indices:
                self.assertEqual(message.message_type, msg_type, msg=str(i))
            else:
                self.assertEqual(message.message_type, self.protocol.default_message_type, msg=str(i))

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
        with open(get_path_for_data_file("undecoded.txt")) as f:
            for line in f:
                self.undecoded_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))

        self.undecoded_protocol.auto_assign_decodings(self.decodings)

        for i, message in enumerate(self.undecoded_protocol.messages):
            if message.plain_hex_str[8:16] == "9a7d9a7d":
                self.assertEqual(message.decoder.name, "DeWhitening Special", msg=str(i))
            elif message.plain_hex_str[8:16] == "67686768":
                self.assertEqual(message.decoder.name, "DeWhitening", msg=str(i))
