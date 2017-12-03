from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh.awre.CommonRange import CommonRange
from urh.awre.FormatFinder import FormatFinder
from urh.awre.components.Address import Address
from urh.awre.components.Component import Component
from urh.awre.components.Flags import Flags
from urh.awre.components.Length import Length
from urh.awre.components.Preamble import Preamble
from urh.awre.components.SequenceNumber import SequenceNumber
from urh.awre.components.Type import Type
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

class TestAWRE(QtTestCase):
    def setUp(self):
        self.field_types = FieldType.default_field_types()

        self.preamble_field_type = self.__field_type_with_function(self.field_types, FieldType.Function.PREAMBLE)
        self.sync_field_type = self.__field_type_with_function(self.field_types, FieldType.Function.SYNC)
        self.length_field_type = self.__field_type_with_function(self.field_types, FieldType.Function.LENGTH)
        self.sequence_number_field_type = self.__field_type_with_function(self.field_types, FieldType.Function.SEQUENCE_NUMBER)
        self.dst_address_field_type = self.__field_type_with_function(self.field_types, FieldType.Function.DST_ADDRESS)
        self.src_address_field_type = self.__field_type_with_function(self.field_types, FieldType.Function.SRC_ADDRESS)

        self.protocol = ProtocolAnalyzer(None)
        with open(get_path_for_data_file("awre_consistent_addresses.txt")) as f:
            for line in f:
                self.protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))
                self.protocol.messages[-1].message_type = self.protocol.default_message_type

        # Assign participants
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        alice_indices = {1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 20, 22, 23, 26, 27, 30, 31, 34, 35, 38, 39, 41}
        for i, message in enumerate(self.protocol.messages):
            message.participant = alice if i in alice_indices else bob

        self.participants = [alice, bob]

        self.zero_crc_protocol = ProtocolAnalyzer(None)
        with open(get_path_for_data_file("awre_zeroed_crc.txt")) as f:
            for line in f:
                self.zero_crc_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))
                self.zero_crc_protocol.messages[-1].message_type = self.protocol.default_message_type

        for i, message in enumerate(self.zero_crc_protocol.messages):
            message.participant = alice if i in alice_indices else bob

    @staticmethod
    def __field_type_with_function(field_types, function) -> FieldType:
        return next(ft for ft in field_types if ft.function == function)

    def test_build_component_order(self):
        expected_default = [Preamble(fieldtypes=[]), Length(fieldtypes=[], length_cluster=None),
                            Address(fieldtypes=[], xor_matrix=None), SequenceNumber(fieldtypes=[]), Type(), Flags()]

        format_finder = FormatFinder(self.protocol)

        for expected, actual in zip(expected_default, format_finder.build_component_order()):
            assert type(expected) == type(actual)

        expected_swapped = [Preamble(fieldtypes=[]), Address(fieldtypes=[],xor_matrix=None),
                            Length(fieldtypes=[], length_cluster=None), SequenceNumber(fieldtypes=[]), Type(), Flags()]
        format_finder.length_component.priority = 2
        format_finder.address_component.priority = 1

        for expected, actual in zip(expected_swapped, format_finder.build_component_order()):
            assert type(expected) == type(actual)

        # Test duplicate Priority
        format_finder.sequence_number_component.priority = 4
        with self.assertRaises(ValueError) as context:
            format_finder.build_component_order()
            self.assertTrue('Duplicate priority' in context.exception)
        format_finder.sequence_number_component.priority = 3
        self.assertTrue(format_finder.build_component_order())

    def test_format_finding_rwe(self):
        preamble_start, preamble_end = 0, 31
        sync_start, sync_end = 32, 63
        length_start, length_end = 64, 71
        ack_address_start, ack_address_end = 72, 95
        dst_address_start, dst_address_end = 88, 111
        src_address_start, src_address_end = 112, 135

        preamble_label = ProtocolLabel(name=self.preamble_field_type.caption, field_type=self.preamble_field_type,
                                       start=preamble_start, end=preamble_end, color_index=0)
        sync_label = ProtocolLabel(name=self.sync_field_type.caption, field_type=self.sync_field_type,
                                   start=sync_start, end=sync_end, color_index=1)
        length_label = ProtocolLabel(name=self.length_field_type.caption, field_type=self.length_field_type,
                                     start=length_start, end=length_end, color_index=2)
        ack_address_label = ProtocolLabel(name=self.dst_address_field_type.caption, field_type=self.dst_address_field_type,
                                          start=ack_address_start, end=ack_address_end, color_index=3)
        dst_address_label = ProtocolLabel(name=self.dst_address_field_type.caption, field_type=self.dst_address_field_type,
                                          start=dst_address_start, end=dst_address_end, color_index=4)
        src_address_label = ProtocolLabel(name=self.src_address_field_type.caption, field_type=self.src_address_field_type,
                                          start=src_address_start, end=src_address_end, color_index=5)

        ff = FormatFinder(protocol=self.protocol, participants=self.participants, field_types=self.field_types)
        ff.perform_iteration()

        self.assertIn(preamble_label, self.protocol.default_message_type)
        self.assertIn(sync_label, self.protocol.default_message_type)
        self.assertIn(length_label, self.protocol.default_message_type)
        self.assertIn(dst_address_label, self.protocol.default_message_type)
        self.assertIn(src_address_label, self.protocol.default_message_type)

        self.assertEqual(len(self.protocol.message_types), 2)
        self.assertEqual(self.protocol.message_types[1].name, "ack")
        self.assertIn(ack_address_label, self.protocol.message_types[1])

        ack_messages = (1, 3, 5, 7, 9, 11, 13, 15, 17, 20)
        for i, msg in enumerate(self.protocol.messages):
            if i in ack_messages:
                self.assertEqual(msg.message_type.name, "ack", msg=i)
            else:
                self.assertEqual(msg.message_type.name, "default", msg=i)


    def test_format_finding_rwe_zeroed_crc(self):
        ff = FormatFinder(self.zero_crc_protocol, self.participants)
        ff.perform_iteration()



    def test_format_finding_enocean(self):
        enocean_protocol = ProtocolAnalyzer(None)
        with open(get_path_for_data_file("enocean_bits.txt")) as f:
            for line in f:
                enocean_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))
                enocean_protocol.messages[-1].message_type = enocean_protocol.default_message_type


        preamble_start = 3
        preamble_end = 10
        sof_start = 11
        sof_end = 14

        preamble_label = ProtocolLabel(name=self.preamble_field_type.caption, field_type=self.preamble_field_type,
                                       start=preamble_start, end=preamble_end, color_index=0)
        sync_label = ProtocolLabel(name=self.sync_field_type.caption, field_type=self.sync_field_type,
                                   start=sof_start, end=sof_end, color_index=1)


        ff = FormatFinder(enocean_protocol, self.participants, field_types=self.field_types)
        ff.perform_iteration()

        self.assertEqual(len(enocean_protocol.message_types), 1)

        self.assertIn(preamble_label, enocean_protocol.default_message_type)
        self.assertIn(sync_label, enocean_protocol.default_message_type)
        self.assertTrue(not any(lbl.name == self.length_field_type.caption for lbl in enocean_protocol.default_message_type))
        self.assertTrue(not any("address" in lbl.name.lower() for lbl in enocean_protocol.default_message_type))

    def test_address_candidate_finding(self):
        fh = CommonRange.from_hex


        candidates_participant_1 = [fh('1b6033'), fh('1b6033fd57'), fh('701b603378e289'), fh('20701b603378e289000c62')]
        candidates_participant_2 = [fh('1b603300'), fh('78e289757e'), fh('7078e2891b6033000000'), fh('207078e2891b6033000000')]

        expected_address1 = '1b6033'
        expected_address2 = '78e289'


        #print(Address.find_candidates(candidates_participant_1))
        #print(Address.find_candidates(candidates_participant_2))
        combined = candidates_participant_1+candidates_participant_2
        combined.sort(key=len)
        score = Address.find_candidates(combined)
        #print(score)
        #print("=================")
        #print(sorted(score, key=lambda k: score[k], reverse=True))
        #print()

        highscored = sorted(score, key=lambda k: score[k], reverse=True)[:2]
        self.assertIn(expected_address1, highscored)
        self.assertIn(expected_address2, highscored)

    def test_message_type_assign(self):
        clusters = {"ack": {1, 17, 3, 20, 5, 7, 9, 11, 13, 15}, "default": {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 19}}
        com = Component(messagetypes=self.protocol.message_types)
        com.assign_messagetypes(self.protocol.messages, clusters)

        for clustername, msg_indices in clusters.items():
            for msg in msg_indices:
                self.assertEqual(self.protocol.messages[msg].message_type.name, clustername, msg=str(msg))

        # do it again and ensure nothing changes
        com.assign_messagetypes(self.protocol.messages, clusters)
        for clustername, msg_indices in clusters.items():
            for msg in msg_indices:
                self.assertEqual(self.protocol.messages[msg].message_type.name, clustername, msg=str(msg))


    def test_choose_candidate(self):

        candidates1 = {'78e289': 8, '207078e2891b6033000000': 1, '57': 1, '20701b603378e289000c62': 1, '1b6033fd57': 1, '1b603300': 3, '7078e2891b6033000000': 2, '78e289757e': 1, '1b6033': 14, '701b603378e289': 2}
        candidates2 = {'1b603300': 4, '701b603378e289': 2, '20701b603378e289000c62': 1, '000': 3, '0000': 19, '1b6033': 11, '78e2890000': 1, '00': 4, '7078e2891b6033000000': 2, '207078e2891b6033000000': 1, '78e289000': 1, '78e289': 7, '0': 7, '1b60330000': 3}

        self.assertEqual(next(Address.choose_candidate_pair(candidates1)), ("1b6033", "78e289"))
        self.assertEqual(next(Address.choose_candidate_pair(candidates2)), ("1b6033", "78e289"))

    def test_format_finding_without_participants(self):
        for msg in self.zero_crc_protocol.messages:
            msg.participant = None

        ff = FormatFinder(self.zero_crc_protocol, [])
        ff.perform_iteration()

    def test_assign_participant_addresses(self):
        clusters = {"ack": {1, 17, 3, 20, 5, 7, 9, 11, 13, 15}, "default": {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 19}}
        com = Component(messagetypes=self.protocol.message_types)
        com.assign_messagetypes(self.protocol.messages, clusters)

        Address.assign_participant_addresses(self.protocol.messages, self.participants, ("78e289", "1b6033"))

        self.assertEqual(self.participants[0].address_hex, "78e289")
        self.assertEqual(self.participants[1].address_hex, "1b6033")
