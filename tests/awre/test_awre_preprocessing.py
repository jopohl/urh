import random

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
import numpy as np


class TestAWREPreprocessing(AWRETestCase):
    def test_very_simple_sync_word_finding(self):
        preamble = "10101010"
        sync = "1101"

        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync)],
            num_messages=(20,),
            data=(lambda i: 10 * i,),
        )

        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )

        possible_syncs = preprocessor.find_possible_syncs()
        # self.save_protocol("very_simple_sync_test", pg)
        self.assertGreaterEqual(len(possible_syncs), 1)
        self.assertEqual(preprocessor.find_possible_syncs()[0], sync)

    def test_simple_sync_word_finding(self):
        preamble = "10101010"
        sync = "1001"

        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync), (preamble + "1010", sync)],
            num_messages=(20, 5),
            data=(lambda i: 10 * i, lambda i: 22 * i),
        )

        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )

        possible_syncs = preprocessor.find_possible_syncs()
        # self.save_protocol("simple_sync_test", pg)
        self.assertGreaterEqual(len(possible_syncs), 1)
        self.assertEqual(preprocessor.find_possible_syncs()[0], sync)

    def test_sync_word_finding_odd_preamble(self):
        preamble = "0101010"
        sync = "1101"
        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync), (preamble + "10", sync)],
            num_messages=(20, 5),
            data=(lambda i: 10 * i, lambda i: i),
        )

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )
        possible_syncs = preprocessor.find_possible_syncs()

        # self.save_protocol("odd_preamble", pg)
        self.assertEqual(preamble[-1] + sync[:-1], possible_syncs[0])

    def test_sync_word_finding_special_preamble(self):
        preamble = "111001110011100"
        sync = "0110"
        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync), (preamble + "10", sync)],
            num_messages=(20, 5),
            data=(lambda i: 10 * i, lambda i: i),
        )

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )
        possible_syncs = preprocessor.find_possible_syncs()

        # self.save_protocol("special_preamble", pg)
        self.assertEqual(sync, possible_syncs[0])

    def test_sync_word_finding_errored_preamble(self):
        preamble = "00010101010"  # first bits are wrong
        sync = "0110"
        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync), (preamble + "10", sync)],
            num_messages=(20, 5),
            data=(lambda i: 10 * i, lambda i: i),
        )

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )
        possible_syncs = preprocessor.find_possible_syncs()

        # self.save_protocol("errored_preamble", pg)
        self.assertIn(preamble[-1] + sync[:-1], possible_syncs)

    def test_sync_word_finding_with_two_sync_words(self):
        preamble = "0xaaaa"
        sync1, sync2 = "0x1234", "0xcafe"
        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync1), (preamble, sync2)],
            num_messages=(15, 10),
            data=(lambda i: 12 * i, lambda i: 16 * i),
        )
        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )
        possible_syncs = preprocessor.find_possible_syncs()
        # self.save_protocol("two_syncs", pg)
        self.assertGreaterEqual(len(possible_syncs), 2)
        self.assertIn(ProtocolGenerator.to_bits(sync1), possible_syncs)
        self.assertIn(ProtocolGenerator.to_bits(sync2), possible_syncs)

    def test_multiple_sync_words(self):
        hex_messages = [
            "aaS1234",
            "aaScafe",
            "aaSdead",
            "aaSbeef",
        ]

        for i in range(1, 256):
            messages = []
            sync = "{0:02x}".format(i)
            if sync.startswith("a"):
                continue

            for msg in hex_messages:
                messages.append(Message.from_plain_hex_str(msg.replace("S", sync)))

            for i in range(1, len(messages)):
                messages[i].message_type = messages[0].message_type

            ff = FormatFinder(messages)
            ff.run()

            self.assertEqual(len(ff.message_types), 1, msg=sync)

            preamble = ff.message_types[0].get_first_label_with_type(
                FieldType.Function.PREAMBLE
            )
            self.assertEqual(preamble.start, 0, msg=sync)
            self.assertEqual(preamble.length, 8, msg=sync)

            sync = ff.message_types[0].get_first_label_with_type(
                FieldType.Function.SYNC
            )
            self.assertEqual(sync.start, 8, msg=sync)
            self.assertEqual(sync.length, 8, msg=sync)

    def test_sync_word_finding_varying_message_length(self):
        hex_messages = [
            "aaaa9a7d0f1337471100009a44ebdd13517bf9",
            "aaaa9a7d4747111337000134a4473c002b909630b11df37e34728c79c60396176aff2b5384e82f31511581d0cbb4822ad1b6734e2372ad5cf4af4c9d6b067e5f7ec359ec443c3b5ddc7a9e",
            "aaaa9a7d0f13374711000205ee081d26c86b8c",
            "aaaa9a7d474711133700037cae4cda789885f88f5fb29adc9acf954cb2850b9d94e7f3b009347c466790e89f2bcd728987d4670690861bbaa120f71f14d4ef8dc738a6d7c30e7d2143c267",
            "aaaa9a7d0f133747110004c2906142300427f3",
        ]

        messages = [Message.from_plain_hex_str(hex_msg) for hex_msg in hex_messages]
        for i in range(1, len(messages)):
            messages[i].message_type = messages[0].message_type

        ff = FormatFinder(messages)
        ff.run()

        self.assertEqual(len(ff.message_types), 1)
        preamble = ff.message_types[0].get_first_label_with_type(
            FieldType.Function.PREAMBLE
        )
        self.assertEqual(preamble.start, 0)
        self.assertEqual(preamble.length, 16)

        sync = ff.message_types[0].get_first_label_with_type(FieldType.Function.SYNC)
        self.assertEqual(sync.start, 16)
        self.assertEqual(sync.length, 16)

    def test_sync_word_finding_common_prefix(self):
        """
        Messages are very similar (odd and even ones are the same)
        However, they do not have two different sync words!
        The algorithm needs to check for a common prefix of the two found sync words

        :return:
        """
        sync = "0x1337"
        num_messages = 10

        alice = Participant("Alice", address_hex="dead01")
        bob = Participant("Bob", address_hex="beef24")

        mb = MessageTypeBuilder("protocol_with_one_message_type")
        mb.add_label(FieldType.Function.PREAMBLE, 72)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x1337"},
            preambles_by_mt={mb.message_type: "10" * 36},
            participants=[alice, bob],
        )

        random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = alice, bob
                data_length = 8
            else:
                source, destination = bob, alice
                data_length = 16
            pg.generate_message(
                data=pg.decimal_to_bits(
                    random.randint(0, 2 ** (data_length - 1)), data_length
                ),
                source=source,
                destination=destination,
            )

        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages]
        )
        possible_syncs = preprocessor.find_possible_syncs()
        # self.save_protocol("sync_by_common_prefix", pg)
        self.assertEqual(len(possible_syncs), 1)

        # +0000 is okay, because this will get fixed by correction in FormatFinder
        self.assertIn(
            possible_syncs[0],
            [ProtocolGenerator.to_bits(sync), ProtocolGenerator.to_bits(sync) + "0000"],
        )

    def test_with_given_preamble_and_sync(self):
        preamble = "10101010"
        sync = "10011"
        pg = self.build_protocol_generator(
            preamble_syncs=[(preamble, sync)],
            num_messages=(20,),
            data=(lambda i: 10 * i,),
        )

        # If we have a odd preamble length, the last bit of the preamble is counted to the sync
        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in pg.protocol.messages],
            existing_message_types={
                i: msg.message_type for i, msg in enumerate(pg.protocol.messages)
            },
        )
        preamble_starts, preamble_lengths, sync_len = preprocessor.preprocess()

        # self.save_protocol("given_preamble", pg)

        self.assertTrue(all(preamble_start == 0 for preamble_start in preamble_starts))
        self.assertTrue(
            all(
                preamble_length == len(preamble) for preamble_length in preamble_lengths
            )
        )
        self.assertEqual(sync_len, len(sync))

    @staticmethod
    def build_protocol_generator(
        preamble_syncs: list, num_messages: tuple, data: tuple
    ) -> ProtocolGenerator:
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

        pg = ProtocolGenerator(
            message_types, preambles_by_mt=preambles_by_mt, syncs_by_mt=syncs_by_mt
        )
        for i, msg_type in enumerate(message_types):
            for j in range(num_messages[i]):
                if callable(data[i]):
                    msg_data = pg.decimal_to_bits(data[i](j), num_bits=8)
                else:
                    msg_data = data[i]

                pg.generate_message(message_type=msg_type, data=msg_data)

        return pg
