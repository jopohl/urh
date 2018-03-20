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
