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
        ack_address = CommonRange(field_type=FieldType.Function.DST_ADDRESS.value, start=72, length=24)
        dst_address = CommonRange(field_type=FieldType.Function.DST_ADDRESS.value, start=88, length=24)
        src_address = CommonRange(field_type=FieldType.Function.SRC_ADDRESS.value, start=112, length=24)

        ff = FormatFinder(protocol=protocol, participants=self.participants)
        # a = next(e for e in ff.engines if isinstance(e, AddressEngine))
        # a.known_addresses_by_participant[0] = np.array([1, 11,  6,  0,  3,  3], dtype=np.uint8)
        ff.perform_iteration()

        sync1, sync2 = "0x9a7d9a7d", "0x67686768"

        preprocessor = Preprocessor(protocol.messages)
        possible_syncs = preprocessor.find_possible_syncs()
        self.assertIn(ProtocolGenerator.to_bits(sync1), possible_syncs)
        self.assertIn(ProtocolGenerator.to_bits(sync2), possible_syncs)

        self.assertEqual(len(ff.message_types), 2)
        mt1 = ff.message_types[0]
        mt2 = ff.message_types[1]

        self.assertIn(preamble, mt1)
        self.assertIn(sync, mt1)
        self.assertIn(length, mt1)
        self.assertIn(dst_address, mt1)
        self.assertIn(src_address, mt1)

        self.assertIn(ack_address, mt2)

        ack_messages = (1, 3, 5, 7, 9, 11, 13, 15, 17, 20)
        for i, msg in enumerate(protocol.messages):
            if i in ack_messages:
                self.assertNotIn(i, mt1.message_indices)
                self.assertIn(i, mt2.message_indices)
            else:
                self.assertIn(i, mt1.message_indices)
                self.assertNotIn(i, mt2.message_indices)

    def test_homematic(self):
        proto_file = get_path_for_data_file("homematic.proto.xml")
        protocol = ProtocolAnalyzer(signal=None, filename=proto_file)
        protocol.message_types = []
        protocol.from_xml_file(filename=proto_file, read_bits=True)
        # prevent interfering with preassinged labels
        protocol.message_types = [MessageType("default")]

        preamble = CommonRange(field_type=FieldType.Function.PREAMBLE.value, start=0, length=32)
        sync = CommonRange(field_type=FieldType.Function.SYNC.value, start=32, length=32)
        length = CommonRange(field_type=FieldType.Function.LENGTH.value, start=64, length=8)
        sequence_number = CommonRange(field_type=FieldType.Function.SEQUENCE_NUMBER.value, start=72, length=8)
        src_address = CommonRange(field_type=FieldType.Function.SRC_ADDRESS.value, start=96, length=24)
        dst_address = CommonRange(field_type=FieldType.Function.DST_ADDRESS.value, start=120, length=24)


        participants = sorted({msg.participant for msg in protocol.messages})
        ff = FormatFinder(protocol, participants=participants)
        ff.perform_iteration()

        self.assertGreater(len(ff.message_types), 0)

        for i, message_type in enumerate(ff.message_types):
            self.assertIn(preamble, message_type, msg=str(i))
            self.assertIn(sync, message_type, msg=str(i))
            self.assertIn(length, message_type, msg=str(i))
            self.assertIn(src_address, message_type, msg=str(i))
            self.assertIn(dst_address, message_type, msg=str(i))
            self.assertIn(sequence_number, message_type, msg=str(i))
