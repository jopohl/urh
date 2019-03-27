from urh.signalprocessing.FieldType import FieldType

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class TestAWREPreprocessing(AWRETestCase):
    def test_very_simple_sync_word_finding(self):
        preamble = "10101010"
        sync = "1101"

        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync)],
                                           num_messages=(20,),
                                           data=(lambda i: 10 * i,))

        preprocessor = Preprocessor(pg.protocol.decoded_bits)

        possible_syncs = preprocessor.find_possible_syncs()
        self.save_protocol("very_simple_sync_test", pg)
        self.assertGreaterEqual(len(possible_syncs), 1)
        self.assertEqual(preprocessor.find_possible_syncs()[0], sync)

    def test_simple_sync_word_finding(self):
        preamble = "10101010"
        sync = "1001"

        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync), (preamble + "1010", sync)],
                                           num_messages=(20, 5),
                                           data=(lambda i: 10 * i, lambda i: 22 * i))

        preprocessor = Preprocessor(pg.protocol.decoded_bits)

        possible_syncs = preprocessor.find_possible_syncs()
        self.save_protocol("simple_sync_test", pg)
        self.assertGreaterEqual(len(possible_syncs), 1)
        self.assertEqual(preprocessor.find_possible_syncs()[0], sync)

    def test_sync_word_finding_odd_preamble(self):
        preamble = "0101010"
        sync = "1101"
        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync), (preamble + "10", sync)],
                                           num_messages=(20, 5),
                                           data=(lambda i: 10 * i, lambda i: i))

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(pg.protocol.decoded_bits)
        possible_syncs = preprocessor.find_possible_syncs()

        self.save_protocol("odd_preamble", pg)
        self.assertEqual(preamble[-1] + sync[:-1], possible_syncs[0])

    def test_sync_word_finding_special_preamble(self):
        preamble = "111001110011100"
        sync = "0110"
        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync), (preamble + "10", sync)],
                                           num_messages=(20, 5),
                                           data=(lambda i: 10 * i, lambda i: i))

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(pg.protocol.decoded_bits)
        possible_syncs = preprocessor.find_possible_syncs()

        self.save_protocol("special_preamble", pg)
        print(possible_syncs)
        self.assertEqual(sync, possible_syncs[0])

    def test_sync_word_finding_errored_preamble(self):
        preamble = "00010101010"  # first bits are wrong
        sync = "0110"
        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync), (preamble + "10", sync)],
                                           num_messages=(20, 5),
                                           data=(lambda i: 10 * i, lambda i: i))

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(pg.protocol.decoded_bits)
        possible_syncs = preprocessor.find_possible_syncs()

        self.save_protocol("errored_preamble", pg)
        print(possible_syncs)
        self.assertEqual(preamble[-1] + sync[:-1], possible_syncs[0])

    def test_sync_word_finding_with_two_sync_words(self):
        preamble = "0xaaaaaaaa"
        sync1, sync2 = "0x9a7d9a7d", "0x67686768"
        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync1), (preamble, sync2)],
                                           num_messages=(15, 10),
                                           data=(lambda i: 12 * i, lambda i: 16 * i))
        preprocessor = Preprocessor(pg.protocol.decoded_bits)
        possible_syncs = preprocessor.find_possible_syncs()
        self.save_protocol("two_syncs", pg)
        self.assertGreaterEqual(len(possible_syncs), 2)
        self.assertIn(ProtocolGenerator.to_bits(sync1), possible_syncs[0:2])
        self.assertIn(ProtocolGenerator.to_bits(sync2), possible_syncs[0:2])

    def test_with_given_preamble_and_sync(self):
        preamble = "10101010"
        sync = "10011"
        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync)],
                                           num_messages=(20,),
                                           data=(lambda i: 10 * i, ))

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(pg.protocol.decoded_bits,
                                    existing_message_types={i: msg.message_type for i, msg in enumerate(pg.protocol.messages)})
        preamble_starts, preamble_lengths, sync_len = preprocessor.preprocess()

        self.save_protocol("given_preamble", pg)

        self.assertTrue(all(preamble_start == 0 for preamble_start in preamble_starts))
        self.assertTrue(all(preamble_length == len(preamble) for preamble_length in preamble_lengths))
        self.assertEqual(sync_len, len(sync))

    def test_paper_examples(self):
        pa = ProtocolAnalyzer(None)
        pa.messages.append(Message.from_plain_bits_str("101010101001"))
        pa.messages.append(Message.from_plain_bits_str("101010100110"))
        pa.messages.append(Message.from_plain_bits_str("10101010101001"))

        preprocessor = Preprocessor(pa.decoded_bits)
        print(preprocessor.get_difference_matrix())

    @staticmethod
    def build_protocol_generator(preamble_syncs: list, num_messages: tuple, data: tuple) -> ProtocolGenerator:
        message_types = []
        preambles_by_mt = dict()
        syncs_by_mt = dict()

        assert len(preamble_syncs) == len(num_messages) == len(data)

        for i, (preamble, sync_word) in enumerate(preamble_syncs):
            assert isinstance(preamble, str)
            assert isinstance(sync_word, str)

            preamble, sync_word = map(ProtocolGenerator.to_bits, (preamble, sync_word))

            mb = MessageTypeBuilder("message type #{0}".format(i))
            mb.add_label(FieldType.Function.PREAMBLE, len(preamble))
            mb.add_label(FieldType.Function.SYNC, len(sync_word))

            message_types.append(mb.message_type)
            preambles_by_mt[mb.message_type] = preamble
            syncs_by_mt[mb.message_type] = sync_word

        pg = ProtocolGenerator(message_types, preambles_by_mt=preambles_by_mt, syncs_by_mt=syncs_by_mt)
        for i, msg_type in enumerate(message_types):
            for j in range(num_messages[i]):
                if callable(data[i]):
                    msg_data = pg.decimal_to_bits(data[i](j), num_bits=8)
                else:
                    msg_data = data[i]

                pg.generate_message(message_type=msg_type, data=msg_data)

        return pg