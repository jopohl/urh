from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.CommonRange import CommonRange
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.SequenceNumberEngine import SequenceNumberEngine
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant


class TestSequenceNumberEngine(AWRETestCase):
    def test_simple_protocol(self):
        """
        Test a simple protocol with
        preamble, sync and increasing sequence number (8 bit) and some constant data

        :return:
        """
        mb = MessageTypeBuilder("simple_seq_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        num_messages = 20

        pg = ProtocolGenerator(
            [mb.message_type], syncs_by_mt={mb.message_type: "0x9a9d"}
        )

        for i in range(num_messages):
            pg.generate_message(data="0xcafe")

        # self.save_protocol("simple_sequence_number", pg)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)

        seq_engine = SequenceNumberEngine(ff.bitvectors, n_gram_length=8)
        highscored_ranges = seq_engine.find()
        self.assertEqual(len(highscored_ranges), 1)

        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 1)
        self.assertGreater(len(ff.message_types[0]), 0)
        self.assertEqual(
            ff.message_types[0].num_labels_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            ),
            1,
        )
        label = ff.message_types[0].get_first_label_with_type(
            FieldType.Function.SEQUENCE_NUMBER
        )
        self.assertEqual(label.start, 24)
        self.assertEqual(label.length, 8)

    def test_16bit_seq_nr(self):
        mb = MessageTypeBuilder("16bit_seq_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        num_messages = 10

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x9a9d"},
            sequence_number_increment=64,
        )

        for i in range(num_messages):
            pg.generate_message(data="0xcafe")

        # self.save_protocol("16bit_seq", pg)

        bitvectors = FormatFinder.get_bitvectors_from_messages(
            pg.protocol.messages, sync_ends=[24] * num_messages
        )
        seq_engine = SequenceNumberEngine(bitvectors, n_gram_length=8)
        highscored_ranges = seq_engine.find()
        self.assertEqual(len(highscored_ranges), 1)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)
        ff.perform_iteration()

        self.assertEqual(len(ff.message_types), 1)
        self.assertGreater(len(ff.message_types[0]), 0)
        self.assertEqual(
            ff.message_types[0].num_labels_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            ),
            1,
        )
        label = ff.message_types[0].get_first_label_with_type(
            FieldType.Function.SEQUENCE_NUMBER
        )
        self.assertEqual(label.start, 24)
        self.assertEqual(label.length, 16)

    def test_16bit_seq_nr_with_zeros_in_first_part(self):
        mb = MessageTypeBuilder("16bit_seq_first_byte_zero_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        num_messages = 10

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x9a9d"},
            sequence_number_increment=1,
        )

        for i in range(num_messages):
            pg.generate_message(data="0xcafe" + "abc" * i)

        # self.save_protocol("16bit_seq_first_byte_zero_test", pg)

        bitvectors = FormatFinder.get_bitvectors_from_messages(
            pg.protocol.messages, sync_ends=[24] * num_messages
        )
        seq_engine = SequenceNumberEngine(bitvectors, n_gram_length=8)
        highscored_ranges = seq_engine.find()
        self.assertEqual(len(highscored_ranges), 1)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)
        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 1)
        self.assertGreater(len(ff.message_types[0]), 0)
        self.assertEqual(
            ff.message_types[0].num_labels_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            ),
            1,
        )
        label = ff.message_types[0].get_first_label_with_type(
            FieldType.Function.SEQUENCE_NUMBER
        )

        # Not consider constants as part of SEQ Nr!
        self.assertEqual(label.start, 40)
        self.assertEqual(label.length, 8)

    def test_no_sequence_number(self):
        """
        Ensure no sequence number is labeled, when it cannot be found

        :return:
        """
        alice = Participant("Alice", address_hex="dead")
        bob = Participant("Bob", address_hex="beef")

        mb = MessageTypeBuilder("protocol_with_one_message_type")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)

        num_messages = 3

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x1337"},
            participants=[alice, bob],
        )

        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = alice, bob
            else:
                source, destination = bob, alice
            pg.generate_message(data="", source=source, destination=destination)

        # self.save_protocol("protocol_1", pg)

        # Delete message type information -> no prior knowledge
        self.clear_message_types(pg.protocol.messages)

        ff = FormatFinder(pg.protocol.messages)
        ff.known_participant_addresses.clear()
        ff.perform_iteration()

        self.assertEqual(len(ff.message_types), 1)

        self.assertEqual(
            ff.message_types[0].num_labels_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            ),
            0,
        )

    def test_sequence_number_little_endian_16_bit(self):
        mb = MessageTypeBuilder("16bit_seq_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        num_messages = 8

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x9a9d"},
            little_endian=True,
            sequence_number_increment=64,
        )

        for i in range(num_messages):
            pg.generate_message(data="0xcafe")

        # self.save_protocol("16bit_litte_endian_seq", pg)

        self.clear_message_types(pg.protocol.messages)
        ff = FormatFinder(pg.protocol.messages)
        ff.perform_iteration()

        self.assertEqual(len(ff.message_types), 1)
        self.assertEqual(
            ff.message_types[0].num_labels_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            ),
            1,
        )
        label = ff.message_types[0].get_first_label_with_type(
            FieldType.Function.SEQUENCE_NUMBER
        )
        self.assertEqual(label.start, 24)
        self.assertEqual(label.length, 16)
