from tests.awre.AWRETestCase import AWRETestCase
from tests.utils_testing import get_path_for_data_file
from urh.awre.CommonRange import CommonRange
from urh.awre.FormatFinder import FormatFinder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
import numpy as np


class TestAWRERealProtocols(AWRETestCase):
    def setUp(self):
        super().setUp()
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        self.participants = [alice, bob]

    def test_format_finding_enocean(self):
        enocean_protocol = ProtocolAnalyzer(None)
        with open(get_path_for_data_file("enocean_bits.txt")) as f:
            for line in f:
                enocean_protocol.messages.append(
                    Message.from_plain_bits_str(line.replace("\n", ""))
                )
                enocean_protocol.messages[
                    -1
                ].message_type = enocean_protocol.default_message_type

        ff = FormatFinder(enocean_protocol.messages)
        ff.perform_iteration()

        message_types = ff.message_types
        self.assertEqual(len(message_types), 1)

        preamble = message_types[0].get_first_label_with_type(
            FieldType.Function.PREAMBLE
        )
        self.assertEqual(preamble.start, 0)
        self.assertEqual(preamble.length, 8)

        sync = message_types[0].get_first_label_with_type(FieldType.Function.SYNC)
        self.assertEqual(sync.start, 8)
        self.assertEqual(sync.length, 4)

        checksum = message_types[0].get_first_label_with_type(
            FieldType.Function.CHECKSUM
        )
        self.assertEqual(checksum.start, 56)
        self.assertEqual(checksum.length, 4)

        self.assertIsNone(
            message_types[0].get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        )
        self.assertIsNone(
            message_types[0].get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        )
        self.assertIsNone(
            message_types[0].get_first_label_with_type(FieldType.Function.LENGTH)
        )
        self.assertIsNone(
            message_types[0].get_first_label_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            )
        )

    def test_format_finding_rwe(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "rwe.proto.xml", return_messages=True
        )
        ff.run()

        sync1, sync2 = "0x9a7d9a7d", "0x67686768"

        preprocessor = Preprocessor(
            [np.array(msg.plain_bits, dtype=np.uint8) for msg in messages]
        )
        possible_syncs = preprocessor.find_possible_syncs()
        self.assertIn(ProtocolGenerator.to_bits(sync1), possible_syncs)
        self.assertIn(ProtocolGenerator.to_bits(sync2), possible_syncs)

        ack_messages = (3, 5, 7, 9, 11, 13, 15, 17, 20)
        ack_message_type = next(
            mt
            for mt, messages in ff.existing_message_types.items()
            if ack_messages[0] in messages
        )
        self.assertTrue(
            all(
                ack_msg in ff.existing_message_types[ack_message_type]
                for ack_msg in ack_messages
            )
        )

        for mt in ff.message_types:
            preamble = mt.get_first_label_with_type(FieldType.Function.PREAMBLE)
            self.assertEqual(preamble.start, 0)
            self.assertEqual(preamble.length, 32)

            sync = mt.get_first_label_with_type(FieldType.Function.SYNC)
            self.assertEqual(sync.start, 32)
            self.assertEqual(sync.length, 32)

            length = mt.get_first_label_with_type(FieldType.Function.LENGTH)
            self.assertEqual(length.start, 64)
            self.assertEqual(length.length, 8)

            dst = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
            self.assertEqual(dst.length, 24)

            if mt == ack_message_type or 1 in ff.existing_message_types[mt]:
                self.assertEqual(dst.start, 72)
            else:
                self.assertEqual(dst.start, 88)

            if mt != ack_message_type and 1 not in ff.existing_message_types[mt]:
                src = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
                self.assertEqual(src.start, 112)
                self.assertEqual(src.length, 24)
            elif 1 in ff.existing_message_types[mt]:
                # long ack
                src = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
                self.assertEqual(src.start, 96)
                self.assertEqual(src.length, 24)

            crc = mt.get_first_label_with_type(FieldType.Function.CHECKSUM)
            self.assertIsNotNone(crc)

    def test_homematic(self):
        proto_file = get_path_for_data_file("homematic.proto.xml")
        protocol = ProtocolAnalyzer(signal=None, filename=proto_file)
        protocol.message_types = []
        protocol.from_xml_file(filename=proto_file, read_bits=True)
        # prevent interfering with preassinged labels
        protocol.message_types = [MessageType("Default")]

        participants = sorted({msg.participant for msg in protocol.messages})

        self.clear_message_types(protocol.messages)
        ff = FormatFinder(protocol.messages, participants=participants)
        ff.known_participant_addresses.clear()
        ff.perform_iteration()

        self.assertGreater(len(ff.message_types), 0)

        for i, message_type in enumerate(ff.message_types):
            preamble = message_type.get_first_label_with_type(
                FieldType.Function.PREAMBLE
            )
            self.assertEqual(preamble.start, 0)
            self.assertEqual(preamble.length, 32)

            sync = message_type.get_first_label_with_type(FieldType.Function.SYNC)
            self.assertEqual(sync.start, 32)
            self.assertEqual(sync.length, 32)

            length = message_type.get_first_label_with_type(FieldType.Function.LENGTH)
            self.assertEqual(length.start, 64)
            self.assertEqual(length.length, 8)

            seq = message_type.get_first_label_with_type(
                FieldType.Function.SEQUENCE_NUMBER
            )
            self.assertEqual(seq.start, 72)
            self.assertEqual(seq.length, 8)

            src = message_type.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
            self.assertEqual(src.start, 96)
            self.assertEqual(src.length, 24)

            dst = message_type.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
            self.assertEqual(dst.start, 120)
            self.assertEqual(dst.length, 24)

            checksum = message_type.get_first_label_with_type(
                FieldType.Function.CHECKSUM
            )
            self.assertEqual(checksum.length, 16)
            self.assertIn("CC1101", checksum.checksum.caption)

            for msg_index in ff.existing_message_types[message_type]:
                msg_len = len(protocol.messages[msg_index])
                self.assertEqual(checksum.start, msg_len - 16)
                self.assertEqual(checksum.end, msg_len)
