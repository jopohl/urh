import copy
import random

from urh.signalprocessing.MessageType import MessageType

from urh.awre.FormatFinder import FormatFinder

from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class TestPartiallyLabeled(AWRETestCase):
    """
    Some tests if there are already information about the message types present

    """

    def test_fully_labeled(self):
        """
        For fully labeled protocol, nothing should be done

        :return:
        """
        protocol = self.__prepare_example_protocol()
        message_types = sorted(
            copy.deepcopy(protocol.message_types), key=lambda x: x.name
        )
        ff = FormatFinder(protocol.messages)
        ff.perform_iteration()
        self.assertEqual(len(message_types), len(ff.message_types))

        for mt1, mt2 in zip(message_types, ff.message_types):
            self.assertTrue(self.__message_types_have_same_labels(mt1, mt2))

    def test_one_message_type_empty(self):
        """
        Empty the "ACK" message type, the labels should be find by FormatFinder

        :return:
        """
        protocol = self.__prepare_example_protocol()
        n_message_types = len(protocol.message_types)
        ack_mt = next(mt for mt in protocol.message_types if mt.name == "ack")
        ack_mt.clear()
        self.assertEqual(len(ack_mt), 0)

        ff = FormatFinder(protocol.messages)
        ff.perform_iteration()
        self.assertEqual(n_message_types, len(ff.message_types))

        self.assertEqual(len(ack_mt), 4, msg=str(ack_mt))

    def test_given_address_information(self):
        """
        Empty both message types and see if addresses are found, when information of participant addresses is given

        :return:
        """
        protocol = self.__prepare_example_protocol()
        self.clear_message_types(protocol.messages)

        ff = FormatFinder(protocol.messages)
        ff.perform_iteration()
        self.assertEqual(2, len(ff.message_types))

        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.PREAMBLE)
        )
        self.assertIsNotNone(
            ff.message_types[1].get_first_label_with_type(FieldType.Function.PREAMBLE)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.SYNC)
        )
        self.assertIsNotNone(
            ff.message_types[1].get_first_label_with_type(FieldType.Function.SYNC)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.LENGTH)
        )
        self.assertIsNotNone(
            ff.message_types[1].get_first_label_with_type(FieldType.Function.LENGTH)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.DST_ADDRESS
            )
        )
        self.assertIsNotNone(
            ff.message_types[1].get_first_label_with_type(
                FieldType.Function.DST_ADDRESS
            )
        )
        self.assertIsNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.SRC_ADDRESS
            )
        )
        self.assertIsNotNone(
            ff.message_types[1].get_first_label_with_type(
                FieldType.Function.SRC_ADDRESS
            )
        )

    def test_type_part_already_labeled(self):
        protocol = self.__prepare_simple_example_protocol()
        self.clear_message_types(protocol.messages)
        ff = FormatFinder(protocol.messages)

        # overlaps type
        ff.message_types[0].add_protocol_label_start_length(32, 8)
        ff.perform_iteration()
        self.assertEqual(1, len(ff.message_types))

        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.PREAMBLE)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.SYNC)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.LENGTH)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.DST_ADDRESS
            )
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.SRC_ADDRESS
            )
        )

    def test_length_part_already_labeled(self):
        protocol = self.__prepare_simple_example_protocol()
        self.clear_message_types(protocol.messages)
        ff = FormatFinder(protocol.messages)

        # overlaps length
        ff.message_types[0].add_protocol_label_start_length(24, 8)
        ff.perform_iteration()
        self.assertEqual(1, len(ff.message_types))

        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.PREAMBLE)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.SYNC)
        )
        self.assertIsNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.LENGTH)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.DST_ADDRESS
            )
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.SRC_ADDRESS
            )
        )

    def test_address_part_already_labeled(self):
        protocol = self.__prepare_simple_example_protocol()
        self.clear_message_types(protocol.messages)
        ff = FormatFinder(protocol.messages)

        # overlaps dst address
        ff.message_types[0].add_protocol_label_start_length(40, 16)
        ff.perform_iteration()
        self.assertEqual(1, len(ff.message_types))

        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.PREAMBLE)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.SYNC)
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(FieldType.Function.LENGTH)
        )
        self.assertIsNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.DST_ADDRESS
            )
        )
        self.assertIsNotNone(
            ff.message_types[0].get_first_label_with_type(
                FieldType.Function.SRC_ADDRESS
            )
        )

    @staticmethod
    def __message_types_have_same_labels(mt1: MessageType, mt2: MessageType):
        if len(mt1) != len(mt2):
            return False

        for i, lbl in enumerate(mt1):
            if lbl != mt2[i]:
                return False

        return True

    def __prepare_example_protocol(self) -> ProtocolAnalyzer:
        alice = Participant("Alice", "A", address_hex="1234")
        bob = Participant("Bob", "B", address_hex="cafe")

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
            pg.generate_message(
                data="",
                message_type=mb_ack.message_type,
                destination=source,
                source=destination,
            )

        # self.save_protocol("labeled_protocol", pg)

        return pg.protocol

    def __prepare_simple_example_protocol(self):
        random.seed(0)
        alice = Participant("Alice", "A", address_hex="1234")
        bob = Participant("Bob", "B", address_hex="cafe")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.TYPE, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x6768"},
            participants=[alice, bob],
        )

        for i in range(10):
            pg.generate_message(
                data="".join([random.choice(["0", "1"]) for _ in range(16)]),
                source=alice,
                destination=bob,
            )
            pg.generate_message(
                data="".join([random.choice(["0", "1"]) for _ in range(8)]),
                source=bob,
                destination=alice,
            )

        return pg.protocol
