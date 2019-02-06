import random

import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.AddressEngine import AddressEngine
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant
from urh.util import util


class TestAddressEngine(AWRETestCase):
    def setUp(self):
        super().setUp()
        self.alice = Participant("Alice", "A", address_hex="1234")
        self.bob = Participant("Bob", "B", address_hex="cafe")

    def test_one_participant(self):
        """
        Test a simple protocol with
        preamble, sync and length field (8 bit) and some random data

        :return:
        """
        mb = MessageTypeBuilder("simple_address_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)

        num_messages_by_data_length = {8: 5, 16: 10, 32: 15}
        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x9a9d"},
                               participants=[self.alice])
        for data_length, num_messages in num_messages_by_data_length.items():
            for i in range(num_messages):
                pg.generate_message(data=pg.decimal_to_bits(22 * i, data_length), source=self.alice)

        self.save_protocol("address_one_participant", pg)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)

        address_engine = AddressEngine(ff.hexvectors, ff.participant_indices)
        address_dict = address_engine.find_addresses()

        self.assertEqual(len(address_dict), 0)

    def test_two_participants(self):
        mb = MessageTypeBuilder("address_two_participants")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)

        num_messages = 50

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x9a9d"},
                               participants=[self.alice, self.bob])

        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = self.alice, self.bob
                data_length = 8
            else:
                source, destination = self.bob, self.alice
                data_length = 16
            pg.generate_message(data=pg.decimal_to_bits(4 * i, data_length), source=source, destination=destination)

        self.save_protocol("address_two_participants", pg)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)

        address_engine = AddressEngine(ff.hexvectors, ff.participant_indices)
        address_dict = address_engine.find_addresses()
        self.assertEqual(len(address_dict), 2)
        addresses_1 = list(map(util.convert_numbers_to_hex_string, address_dict[0]))
        addresses_2 = list(map(util.convert_numbers_to_hex_string, address_dict[1]))
        self.assertIn(self.alice.address_hex, addresses_1)
        self.assertIn(self.alice.address_hex, addresses_2)
        self.assertIn(self.bob.address_hex, addresses_1)
        self.assertIn(self.bob.address_hex, addresses_2)

        ff.known_participant_addresses.clear()
        self.assertEqual(len(ff.known_participant_addresses), 0)
        ff.perform_iteration()

        self.assertEqual(len(ff.known_participant_addresses), 2)
        self.assertIn(bytes([int(h, 16) for h in self.alice.address_hex]), ff.known_participant_addresses.values())
        self.assertIn(bytes([int(h, 16) for h in self.bob.address_hex]), ff.known_participant_addresses.values())
        print(ff.known_participant_addresses)

        self.assertEqual(len(ff.message_types), 1)
        mt = ff.message_types[0]
        dst_addr = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        self.assertIsNotNone(dst_addr)
        self.assertEqual(dst_addr.start, 32)
        self.assertEqual(dst_addr.length, 16)
        src_addr = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        self.assertIsNotNone(src_addr)
        self.assertEqual(src_addr.start, 48)
        self.assertEqual(src_addr.length, 16)

    def test_two_participants_with_ack_messages(self):
        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 8)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)

        num_messages = 50

        pg = ProtocolGenerator([mb.message_type, mb_ack.message_type],
                               syncs_by_mt={mb.message_type: "0x6768", mb_ack.message_type: "0x6768"},
                               participants=[self.alice, self.bob])

        random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = self.alice, self.bob
                data_length = 8
            else:
                source, destination = self.bob, self.alice
                data_length = 16
            pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 2 ** (data_length - 1)), data_length),
                                source=source, destination=destination)
            pg.generate_message(data="", message_type=mb_ack.message_type, destination=source, source=destination)

        self.save_protocol("address_two_participants_with_acks", pg)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)
        address_engine = AddressEngine(ff.hexvectors, ff.participant_indices)
        address_dict = address_engine.find_addresses()
        self.assertEqual(len(address_dict), 2)
        addresses_1 = list(map(util.convert_numbers_to_hex_string, address_dict[0]))
        addresses_2 = list(map(util.convert_numbers_to_hex_string, address_dict[1]))
        self.assertIn(self.alice.address_hex, addresses_1)
        self.assertIn(self.alice.address_hex, addresses_2)
        self.assertIn(self.bob.address_hex, addresses_1)
        self.assertIn(self.bob.address_hex, addresses_2)

        ff.known_participant_addresses.clear()
        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 2)
        mt = ff.message_types[1]
        dst_addr = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        self.assertIsNotNone(dst_addr)
        self.assertEqual(dst_addr.start, 32)
        self.assertEqual(dst_addr.length, 16)
        src_addr = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        self.assertIsNotNone(src_addr)
        self.assertEqual(src_addr.start, 48)
        self.assertEqual(src_addr.length, 16)

        mt = ff.message_types[0]
        dst_addr = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        self.assertIsNotNone(dst_addr)
        self.assertEqual(dst_addr.start, 32)
        self.assertEqual(dst_addr.length, 16)

    def test_two_participants_with_ack_messages_and_type(self):
        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.TYPE, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 8)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)

        num_messages = 50

        pg = ProtocolGenerator([mb.message_type, mb_ack.message_type],
                               syncs_by_mt={mb.message_type: "0x6768", mb_ack.message_type: "0x6768"},
                               participants=[self.alice, self.bob])

        random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = self.alice, self.bob
                data_length = 8
            else:
                source, destination = self.bob, self.alice
                data_length = 16
            pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 2 ** (data_length - 1)), data_length),
                                source=source, destination=destination)
            pg.generate_message(data="", message_type=mb_ack.message_type, destination=source, source=destination)

        self.save_protocol("address_two_participants_with_acks_and_types", pg)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)
        address_engine = AddressEngine(ff.hexvectors, ff.participant_indices)
        address_dict = address_engine.find_addresses()
        self.assertEqual(len(address_dict), 2)
        addresses_1 = list(map(util.convert_numbers_to_hex_string, address_dict[0]))
        addresses_2 = list(map(util.convert_numbers_to_hex_string, address_dict[1]))
        self.assertIn(self.alice.address_hex, addresses_1)
        self.assertIn(self.alice.address_hex, addresses_2)
        self.assertIn(self.bob.address_hex, addresses_1)
        self.assertIn(self.bob.address_hex, addresses_2)

        ff.known_participant_addresses.clear()
        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 2)
        mt = ff.message_types[1]
        dst_addr = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        self.assertIsNotNone(dst_addr)
        self.assertEqual(dst_addr.start, 40)
        self.assertEqual(dst_addr.length, 16)
        src_addr = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        self.assertIsNotNone(src_addr)
        self.assertEqual(src_addr.start, 56)
        self.assertEqual(src_addr.length, 16)

        mt = ff.message_types[0]
        dst_addr = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        self.assertIsNotNone(dst_addr)
        self.assertEqual(dst_addr.start, 32)
        self.assertEqual(dst_addr.length, 16)

    def test_find_common_sub_sequence(self):
        from urh.cythonext import awre_util
        str1 = "0612345678"
        str2 = "0756781234"

        seq1 = np.array(list(map(int, str1)), dtype=np.uint8, order="C")
        seq2 = np.array(list(map(int, str2)), dtype=np.uint8, order="C")

        indices = awre_util.find_longest_common_sub_sequence_indices(seq1, seq2)
        self.assertEqual(len(indices), 2)
        for ind in indices:
            s = str1[slice(*ind)]
            self.assertIn(s, ("5678", "1234"))
            self.assertIn(s, str1)
            self.assertIn(s, str2)

    def test_find_first_occurrence(self):
        from urh.cythonext import awre_util
        str1 = "00" * 100 + "1234500012345" + "00" * 100
        str2 = "12345"

        seq1 = np.array(list(map(int, str1)), dtype=np.uint8, order="C")
        seq2 = np.array(list(map(int, str2)), dtype=np.uint8, order="C")
        indices = awre_util.find_occurrences(seq1, seq2)
        self.assertEqual(len(indices), 2)
        index = indices[0]
        self.assertEqual(str1[index:index + len(str2)], str2)
        self.assertEqual(awre_util.find_occurrences(seq1, np.ones(10, dtype=np.uint8)), [])
