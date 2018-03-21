from tests.awre.AWRETestCase import AWRETestCase
from tests.utils_testing import get_path_for_data_file
from urh.awre.CommonRange import CommonRange
from urh.awre.FormatFinder import FormatFinder
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


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
                enocean_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))
                enocean_protocol.messages[-1].message_type = enocean_protocol.default_message_type

        preamble = CommonRange(field_type=FieldType.Function.PREAMBLE.value, start=3, length=8)
        sync = CommonRange(field_type=FieldType.Function.SYNC.value, start=11, length=4)

        ff = FormatFinder(enocean_protocol, self.participants)
        ff.perform_iteration()

        message_types = ff.message_types
        self.assertEqual(len(message_types), 1)

        self.assertIn(preamble, message_types[0])
        self.assertIn(sync, message_types[0])
        print(message_types[0])
        self.assertTrue(not any("address" in cr.field_type.lower() for cr in message_types[0]))

    def test_format_finding_rwe(self):
        protocol = ProtocolAnalyzer(None)
        with open(get_path_for_data_file("awre_consistent_addresses.txt")) as f:
            for line in f:
                protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", "")))
                protocol.messages[-1].message_type = protocol.default_message_type

        alice_indices = {1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 20, 22, 23, 26, 27, 30, 31, 34, 35, 38, 39, 41}
        for i, message in enumerate(protocol.messages):
            message.participant = self.participants[0] if i in alice_indices else self.participants[1]

        preamble = CommonRange(field_type=FieldType.Function.PREAMBLE.value, start=0, length=32)
        sync = CommonRange(field_type=FieldType.Function.SYNC.value, start=32, length=32)
        length = CommonRange(field_type=FieldType.Function.LENGTH.value, start=64, length=8)
        ack_address= CommonRange(field_type=FieldType.Function.DST_ADDRESS.value, start=72, length=24)
        dst_address = CommonRange(field_type=FieldType.Function.DST_ADDRESS.value, start=88, length=24)
        src_address = CommonRange(field_type=FieldType.Function.SRC_ADDRESS.value, start=112, length=24)

        ff = FormatFinder(protocol=protocol, participants=self.participants)
        ff.perform_iteration()

        # TODO: Make algorithm deal with multiple message types
        # self.assertEqual(len(ff.message_types), 2)
        # mt1 = ff.message_types[0]
        # mt2 = ff.message_types[1]
        #
        # self.assertIn(preamble, mt1)
        # self.assertIn(sync, mt1)
        # self.assertIn(length, mt1)
        # self.assertIn(dst_address, mt1)
        # self.assertIn(src_address, mt1)

        # self.assertEqual(len(self.protocol.message_types), 2)
        # self.assertEqual(self.protocol.message_types[1].name, "ack")
        # self.assertIn(ack_address_label, self.protocol.message_types[1])
        #
        # ack_messages = (1, 3, 5, 7, 9, 11, 13, 15, 17, 20)
        # for i, msg in enumerate(self.protocol.messages):
        #     if i in ack_messages:
        #         self.assertEqual(msg.message_type.name, "ack", msg=i)
        #     else:
        #         self.assertEqual(msg.message_type.name, "default", msg=i)
