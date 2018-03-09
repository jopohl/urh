from tests.awre.AWRETestCase import AWRETestCase
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

        preprocessor = Preprocessor(pg.protocol.messages)

        possible_syncs = preprocessor.find_possible_syncs()
        self.save_protocol("very_simple_sync_test", pg)
        self.assertGreaterEqual(len(possible_syncs), 1)
        self.assertEqual(preprocessor.find_possible_syncs()[0], sync)

    def test_simple_sync_word_finding(self):
        preamble = "10101010"
        sync = "1001"

        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync), (preamble + "1010", sync)],
                                           num_messages=(20, 5),
                                           data=(lambda i: 10 * i, lambda i: 22*i))

        preprocessor = Preprocessor(pg.protocol.messages)

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
        preprocessor = Preprocessor(pg.protocol.messages)
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
        preprocessor = Preprocessor(pg.protocol.messages)
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
        preprocessor = Preprocessor(pg.protocol.messages)
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
        preprocessor = Preprocessor(pg.protocol.messages)
        possible_syncs = preprocessor.find_possible_syncs()
        self.save_protocol("two_syncs", pg)
        self.assertGreaterEqual(len(possible_syncs), 2)
        self.assertIn(ProtocolGenerator.to_bits(sync1), possible_syncs[0:2])
        self.assertIn(ProtocolGenerator.to_bits(sync2), possible_syncs[0:2])

    def test_very_simple_sync_alignment(self):
        """
        Here we test the most simple case:
        Preamble 10101010 Sync 1001 No errors
        :return:
        """
        preamble = "10101010"
        sync = "1001"

        pg = self.build_protocol_generator(preamble_syncs=[(preamble, sync), (preamble + "10", sync), (preamble[2:], sync)],
                                           num_messages=(20, 5, 5),
                                           data=(lambda i: 10 * i, lambda i: 22 * i, lambda i: 33 * i))

        # TODO Add a message type where first bit of preamble is missing

        self.save_protocol("simple_preamble", pg)

        preprocessor = Preprocessor(pg.protocol.messages)
        preamble_lengths = preprocessor.get_preamble_lengths_from_sync_words([sync])
        preprocessor.align_messages(preamble_lengths)

        self.save_protocol("simple_preamble_cropped", pg)

        # # Now the longer preambles should be cropped and the shorter should be padded
        for i, msg in enumerate(pg.protocol.messages):
            self.assertTrue(msg.decoded_bits_str.startswith(preamble + sync), msg=str(i))

    def test_paper_examples(self):
        pa = ProtocolAnalyzer(None)
        pa.messages.append(Message.from_plain_bits_str("101010101001"))
        pa.messages.append(Message.from_plain_bits_str("101010100110"))
        pa.messages.append(Message.from_plain_bits_str("10101010101001"))

        preprocessor = Preprocessor(pa.messages)
        print(preprocessor.get_difference_matrix())

