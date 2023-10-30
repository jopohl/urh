import random
from array import array

import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from tests.utils_testing import get_path_for_data_file
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.AddressEngine import AddressEngine
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
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
        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x9a9d"},
            participants=[self.alice],
        )
        for data_length, num_messages in num_messages_by_data_length.items():
            for i in range(num_messages):
                pg.generate_message(
                    data=pg.decimal_to_bits(22 * i, data_length), source=self.alice
                )

        # self.save_protocol("address_one_participant", pg)

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

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x9a9d"},
            participants=[self.alice, self.bob],
        )

        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = self.alice, self.bob
                data_length = 8
            else:
                source, destination = self.bob, self.alice
                data_length = 16
            pg.generate_message(
                data=pg.decimal_to_bits(4 * i, data_length),
                source=source,
                destination=destination,
            )

        # self.save_protocol("address_two_participants", pg)

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
        self.assertIn(
            bytes([int(h, 16) for h in self.alice.address_hex]),
            map(bytes, ff.known_participant_addresses.values()),
        )
        self.assertIn(
            bytes([int(h, 16) for h in self.bob.address_hex]),
            map(bytes, ff.known_participant_addresses.values()),
        )

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

        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type],
            syncs_by_mt={mb.message_type: "0x6768", mb_ack.message_type: "0x6768"},
            participants=[self.alice, self.bob],
        )

        random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = self.alice, self.bob
                data_length = 8
            else:
                source, destination = self.bob, self.alice
                data_length = 16
            pg.generate_message(
                data=pg.decimal_to_bits(
                    random.randint(0, 2 ** (data_length - 1)), data_length
                ),
                source=source,
                destination=destination,
            )
            pg.generate_message(
                data="",
                message_type=mb_ack.message_type,
                destination=source,
                source=destination,
            )

        # self.save_protocol("address_two_participants_with_acks", pg)

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

        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type],
            syncs_by_mt={mb.message_type: "0x6768", mb_ack.message_type: "0x6768"},
            participants=[self.alice, self.bob],
        )

        random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = self.alice, self.bob
                data_length = 8
            else:
                source, destination = self.bob, self.alice
                data_length = 16
            pg.generate_message(
                data=pg.decimal_to_bits(
                    random.randint(0, 2 ** (data_length - 1)), data_length
                ),
                source=source,
                destination=destination,
            )
            pg.generate_message(
                data="",
                message_type=mb_ack.message_type,
                destination=source,
                source=destination,
            )

        # self.save_protocol("address_two_participants_with_acks_and_types", pg)

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

    def test_three_participants_with_ack(self):
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="4711")
        carl = Participant("Carl", address_hex="cafe")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 16)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)

        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type],
            syncs_by_mt={mb.message_type: "0x9a7d", mb_ack.message_type: "0x9a7d"},
            preambles_by_mt={mb.message_type: "10" * 8, mb_ack.message_type: "10" * 8},
            participants=[alice, bob, carl],
        )

        i = -1
        while len(pg.protocol.messages) < 20:
            i += 1
            source = pg.participants[i % len(pg.participants)]
            destination = pg.participants[(i + 1) % len(pg.participants)]
            if i % 2 == 0:
                data_bytes = 8
            else:
                data_bytes = 16

            data = "".join(random.choice(["0", "1"]) for _ in range(data_bytes * 8))
            pg.generate_message(data=data, source=source, destination=destination)

            if "ack" in (msg_type.name for msg_type in pg.protocol.message_types):
                pg.generate_message(
                    message_type=1, data="", source=destination, destination=source
                )

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)
        ff.known_participant_addresses.clear()
        self.assertEqual(len(ff.known_participant_addresses), 0)
        ff.run()

        # Since there are ACKS in this protocol, the engine must be able to assign the correct participant addresses
        # IN CORRECT ORDER!
        self.assertEqual(
            util.convert_numbers_to_hex_string(ff.known_participant_addresses[0]),
            "1337",
        )
        self.assertEqual(
            util.convert_numbers_to_hex_string(ff.known_participant_addresses[1]),
            "4711",
        )
        self.assertEqual(
            util.convert_numbers_to_hex_string(ff.known_participant_addresses[2]),
            "cafe",
        )

    def test_protocol_with_acks_and_checksum(self):
        proto_file = get_path_for_data_file("ack_frames_with_crc.proto.xml")
        protocol = ProtocolAnalyzer(signal=None, filename=proto_file)
        protocol.from_xml_file(filename=proto_file, read_bits=True)

        self.clear_message_types(protocol.messages)

        ff = FormatFinder(protocol.messages)
        ff.known_participant_addresses.clear()

        ff.run()
        self.assertEqual(
            util.convert_numbers_to_hex_string(ff.known_participant_addresses[0]),
            "1337",
        )
        self.assertEqual(
            util.convert_numbers_to_hex_string(ff.known_participant_addresses[1]),
            "4711",
        )

        for mt in ff.message_types:
            preamble = mt.get_first_label_with_type(FieldType.Function.PREAMBLE)
            self.assertEqual(preamble.start, 0)
            self.assertEqual(preamble.length, 16)
            sync = mt.get_first_label_with_type(FieldType.Function.SYNC)
            self.assertEqual(sync.start, 16)
            self.assertEqual(sync.length, 16)
            length = mt.get_first_label_with_type(FieldType.Function.LENGTH)
            self.assertEqual(length.start, 32)
            self.assertEqual(length.length, 8)

    def test_address_engine_performance(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "35_messages.proto.xml", return_messages=True
        )

        engine = AddressEngine(ff.hexvectors, ff.participant_indices)
        engine.find()

    def test_paper_example(self):
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        participants = [alice, bob]
        msg1 = Message.from_plain_hex_str("aabb1234")
        msg1.participant = alice
        msg2 = Message.from_plain_hex_str("aabb6789")
        msg2.participant = alice
        msg3 = Message.from_plain_hex_str("bbaa4711")
        msg3.participant = bob
        msg4 = Message.from_plain_hex_str("bbaa1337")
        msg4.participant = bob

        protocol = ProtocolAnalyzer(None)
        protocol.messages.extend([msg1, msg2, msg3, msg4])
        # self.save_protocol("paper_example", protocol)

        bitvectors = FormatFinder.get_bitvectors_from_messages(protocol.messages)
        hexvectors = FormatFinder.get_hexvectors(bitvectors)
        address_engine = AddressEngine(
            hexvectors,
            participant_indices=[
                participants.index(msg.participant) for msg in protocol.messages
            ],
        )

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
        self.assertEqual(str1[index : index + len(str2)], str2)

        # Test with ignoring indices
        indices = awre_util.find_occurrences(
            seq1, seq2, array("L", list(range(0, 205)))
        )
        self.assertEqual(len(indices), 1)

        # Test with ignoring indices
        indices = awre_util.find_occurrences(
            seq1, seq2, array("L", list(range(0, 210)))
        )
        self.assertEqual(len(indices), 0)

        self.assertEqual(
            awre_util.find_occurrences(seq1, np.ones(10, dtype=np.uint8)), []
        )
