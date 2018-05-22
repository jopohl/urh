from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.SequenceNumberEngine import SequenceNumberEngine
from urh.signalprocessing.FieldType import FieldType


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

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x9a9d"})

        for i in range(num_messages):
            pg.generate_message(data="0xcafe")

        self.save_protocol("simple_sequence_number", pg)

        ff = FormatFinder(pg.protocol)

        seq_engine = SequenceNumberEngine(ff.bitvectors)
        highscored_ranges = seq_engine.find(n_gram_length=8)
        # self.assertEqual(len(highscored_ranges), 3)
        #
        # ff.perform_iteration()
        # self.assertEqual(len(ff.message_types), 1)
        # self.assertGreater(len(ff.message_types[0]), 0)
        # label = next(lbl for lbl in ff.message_types[0]
        #              if lbl.field_type == "length")
        # self.assertIsInstance(label, CommonRange)
        # self.assertEqual(label.field_type, "length")
        # self.assertEqual(label.bit_start, 24)
        # self.assertEqual(label.length, 8)

    def test_16bit_seq_nr(self):
        mb = MessageTypeBuilder("16bit_seq_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        num_messages = 1024

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x9a9d"})

        for i in range(num_messages):
            pg.generate_message(data="0xcafe")

        self.save_protocol("16bit_seq", pg)

        bitvectors = FormatFinder.get_bitvectors_from_messages(pg.protocol.messages, sync_ends=[24]*num_messages)
        seq_engine = SequenceNumberEngine(bitvectors)
        highscored_ranges = seq_engine.find(n_gram_length=8)