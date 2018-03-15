import random

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.CommonRange import CommonRange, EmptyCommonRange
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.LengthEngine import LengthEngine
from urh.signalprocessing.FieldType import FieldType


class TestLengthEngine(AWRETestCase):
    def test_score_common_range(self):
        common_range = CommonRange(0, 8, "0000011")
        target_value = 1
        le = LengthEngine([])
        print(le.score_range(common_range, target_value))

    def test_simple_protocol(self):
        """
        Test a simple protocol with
        preamble, sync and length field (8 bit) and some random data
        :return:
        """
        mb = MessageTypeBuilder("simple_length_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)

        num_messages_by_data_length = {8: 5, 16: 10, 32: 15}
        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x9a9d"})
        for data_length, num_messages in num_messages_by_data_length.items():
            for i in range(num_messages):
                pg.generate_message(data=pg.decimal_to_bits(5*i, data_length))

        self.save_protocol("simple_length", pg)

        ff = FormatFinder(pg.protocol)

        length_engine = LengthEngine(ff.bitvectors)
        highscored_ranges = length_engine.find(n_gram_length=8)
        self.assertEqual(len(highscored_ranges), 3)

        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 1)
        self.assertGreater(len(ff.message_types[0]), 0)
        label = next(lbl for lbl in ff.message_types[0]
                     if lbl.field_type == "Length")
        self.assertIsInstance(label, CommonRange)
        self.assertEqual(label.field_type, "Length")
        self.assertEqual(label.start, 24)
        self.assertEqual(label.length, 8)

    def test_easy_protocol(self):
        """
        preamble, sync, sequence number, length field (8 bit) and some random data
        :return:
        """
        mb = MessageTypeBuilder("easy_length_test")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        num_messages_by_data_length = {32: 10, 64: 15, 16: 5, 24: 7}
        pg = ProtocolGenerator([mb.message_type],
                               preambles_by_mt={mb.message_type: "10"*8},
                               syncs_by_mt={mb.message_type: "0xcafe"})
        for data_length, num_messages in num_messages_by_data_length.items():
            for i in range(num_messages):
                if i % 4 == 0:
                    data = "1" * data_length
                elif i % 4 == 1:
                    data = "0" * data_length
                elif i % 4 == 2:
                    data = "10" * (data_length//2)
                else:
                    data = "01" * (data_length//2)

                pg.generate_message(data=data)

        self.save_protocol("easy_length", pg)

        ff = FormatFinder(pg.protocol)

        length_engine = LengthEngine(ff.bitvectors)
        highscored_ranges = length_engine.find(n_gram_length=8)
        self.assertEqual(len(highscored_ranges), 4)

        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 1)
        self.assertGreater(len(ff.message_types[0]), 0)
        label = next(lbl for lbl in ff.message_types[0]
                     if lbl.field_type == "Length")
        self.assertIsInstance(label, CommonRange)
        self.assertEqual(label.field_type, "Length")
        self.assertEqual(label.start, 32)
        self.assertEqual(label.length, 8)

    def test_medium_protocol(self):
        """
        Protocol with two message types. Length field only present in one of them
        :return:
        """
        mb1 = MessageTypeBuilder("data")
        mb1.add_label(FieldType.Function.PREAMBLE, 8)
        mb1.add_label(FieldType.Function.SYNC, 8)
        mb1.add_label(FieldType.Function.LENGTH, 8)
        mb1.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        mb2 = MessageTypeBuilder("ack")
        mb2.add_label(FieldType.Function.PREAMBLE, 8)
        mb2.add_label(FieldType.Function.SYNC, 8)

        pg = ProtocolGenerator([mb1.message_type, mb2.message_type],
                               syncs_by_mt={mb1.message_type: "11110011",
                                            mb2.message_type: "11110011"})
        num_messages_by_data_length = {8: 5, 16: 10, 32: 5}
        for data_length, num_messages in num_messages_by_data_length.items():
            for i in range(num_messages):
                pg.generate_message(data=pg.decimal_to_bits(10*i, data_length), message_type=mb1.message_type)
                pg.generate_message(message_type=mb2.message_type)

        self.save_protocol("medium_length", pg)

        ff = FormatFinder(pg.protocol)

        ff.perform_iteration()
        self.assertEqual(len(ff.message_types), 2)
        length_mt = next(mt for mt in ff.message_types if EmptyCommonRange("Length") not in mt)
        length_range = next(rng for rng in length_mt if rng.field_type == "Length")

        for i, sync_end in enumerate(ff.sync_ends):
            self.assertEqual(sync_end, 16, msg=str(i))

        self.assertEqual(16, length_range.start)
        self.assertEqual(8, length_range.length)

    def test_nibble_protocol(self):
        """
        Nibble protocol
        :return:
        """