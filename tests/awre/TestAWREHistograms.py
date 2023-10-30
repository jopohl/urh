import random
from collections import defaultdict

import matplotlib.pyplot as plt

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.Histogram import Histogram
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant

SHOW_PLOTS = True


class TestAWREHistograms(AWRETestCase):
    def test_very_simple_protocol(self):
        """
        Test a very simple protocol consisting just of a preamble, sync and some random data
        :return:
        """
        mb = MessageTypeBuilder("very_simple_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 8)

        num_messages = 10

        pg = ProtocolGenerator([mb.message_type], syncs_by_mt={mb.message_type: "0x9a"})
        for _ in range(num_messages):
            pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 255), 8))

        self.save_protocol("very_simple", pg)

        h = Histogram(FormatFinder.get_bitvectors_from_messages(pg.protocol.messages))
        if SHOW_PLOTS:
            h.plot()

    def test_simple_protocol(self):
        """
        Test a simple protocol with preamble, sync and length field and some random data
        :return:
        """
        mb = MessageTypeBuilder("simple_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)

        num_messages_by_data_length = {8: 5, 16: 10, 32: 15}
        pg = ProtocolGenerator(
            [mb.message_type], syncs_by_mt={mb.message_type: "0x9a9d"}
        )
        for data_length, num_messages in num_messages_by_data_length.items():
            for _ in range(num_messages):
                pg.generate_message(
                    data=pg.decimal_to_bits(
                        random.randint(0, 2**data_length - 1), data_length
                    )
                )

        self.save_protocol("simple", pg)

        plt.subplot("221")
        plt.title("All messages")
        format_finder = FormatFinder(pg.protocol.messages)

        for i, sync_end in enumerate(format_finder.sync_ends):
            self.assertEqual(sync_end, 24, msg=str(i))

        h = Histogram(format_finder.bitvectors)
        h.subplot_on(plt)

        bitvectors = FormatFinder.get_bitvectors_from_messages(pg.protocol.messages)
        bitvectors_by_length = defaultdict(list)
        for bitvector in bitvectors:
            bitvectors_by_length[len(bitvector)].append(bitvector)

        for i, (message_length, bitvectors) in enumerate(bitvectors_by_length.items()):
            plt.subplot(2, 2, i + 2)
            plt.title(
                "Messages with length {} ({})".format(message_length, len(bitvectors))
            )
            Histogram(bitvectors).subplot_on(plt)

        if SHOW_PLOTS:
            plt.show()

    def test_medium_protocol(self):
        """
        Test a protocol with preamble, sync, length field, 2 participants and addresses and seq nr and random data
        :return:
        """
        mb = MessageTypeBuilder("medium_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 8)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        alice = Participant("Alice", "A", "1234", color_index=0)
        bob = Participant("Bob", "B", "5a9d", color_index=1)

        num_messages = 100
        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x1c"},
            little_endian=False,
        )
        for i in range(num_messages):
            len_data = random.randint(1, 5)
            data = "".join(
                pg.decimal_to_bits(random.randint(0, 2**8 - 1), 8)
                for _ in range(len_data)
            )
            if i % 2 == 0:
                source, dest = alice, bob
            else:
                source, dest = bob, alice
            pg.generate_message(data=data, source=source, destination=dest)

        self.save_protocol("medium", pg)

        plt.subplot(2, 2, 1)
        plt.title("All messages")
        bitvectors = FormatFinder.get_bitvectors_from_messages(pg.protocol.messages)
        h = Histogram(bitvectors)
        h.subplot_on(plt)

        for i, (participant, bitvectors) in enumerate(
            sorted(self.get_bitvectors_by_participant(pg.protocol.messages).items())
        ):
            plt.subplot(2, 2, i + 3)
            plt.title(
                "Messages with participant {} ({})".format(
                    participant.shortname, len(bitvectors)
                )
            )
            Histogram(bitvectors).subplot_on(plt)

        if SHOW_PLOTS:
            plt.show()

    def get_bitvectors_by_participant(self, messages):
        import numpy as np

        result = defaultdict(list)
        for msg in messages:  # type: Message
            result[msg.participant].append(
                np.array(msg.decoded_bits, dtype=np.uint8, order="C")
            )
        return result

    def test_ack_protocol(self):
        """
        Test a protocol with acks
        :return:
        """
        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 8)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 8)
        mb_ack.add_label(FieldType.Function.SYNC, 8)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)

        alice = Participant("Alice", "A", "1234", color_index=0)
        bob = Participant("Bob", "B", "5a9d", color_index=1)

        num_messages = 50
        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type],
            syncs_by_mt={mb.message_type: "0xbf", mb_ack.message_type: "0xbf"},
            little_endian=False,
        )
        for i in range(num_messages):
            if i % 2 == 0:
                source, dest = alice, bob
            else:
                source, dest = bob, alice
            pg.generate_message(data="0xffff", source=source, destination=dest)
            pg.generate_message(
                data="",
                source=dest,
                destination=source,
                message_type=mb_ack.message_type,
            )

        self.save_protocol("proto_with_acks", pg)

        plt.subplot(2, 2, 1)
        plt.title("All messages")
        bitvectors = FormatFinder.get_bitvectors_from_messages(pg.protocol.messages)
        h = Histogram(bitvectors)
        h.subplot_on(plt)

        for i, (participant, bitvectors) in enumerate(
            sorted(self.get_bitvectors_by_participant(pg.protocol.messages).items())
        ):
            plt.subplot(2, 2, i + 3)
            plt.title(
                "Messages with participant {} ({})".format(
                    participant.shortname, len(bitvectors)
                )
            )
            Histogram(bitvectors).subplot_on(plt)

        if SHOW_PLOTS:
            plt.show()
