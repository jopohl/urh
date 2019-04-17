from urh.awre.FormatFinder import FormatFinder

from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.signalprocessing.Participant import Participant


class TestGeneratedProtocols( AWRETestCase):
    def test_without_preamble(self):
        alice = Participant("Alice", address_hex="24")
        broadcast = Participant("Broadcast", address_hex="ff")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x8e88"},
                               preambles_by_mt={mb.message_type: "10" * 8},
                               participants=[alice, broadcast])

        for i in range(20):
            data_bits = 16 if i % 2 == 0 else 32
            source = pg.participants[i%2]
            destination = pg.participants[(i+1)%2]
            pg.generate_message(data="1010"*(data_bits//4), source=source, destination=destination)

        self.save_protocol("without_preamble", pg)
        self.clear_message_types(pg.messages)
        ff = FormatFinder(pg.messages)
        ff.known_participant_addresses.clear()

        ff.run()
        print(ff.message_types)
        self.assertEqual(len(ff.message_types), 1)

        mt = ff.message_types[0]
        sync = mt.get_first_label_with_type(FieldType.Function.SYNC)
        self.assertEqual(sync.start, 0)
        self.assertEqual(sync.length, 16)

        length = mt.get_first_label_with_type(FieldType.Function.LENGTH)
        self.assertEqual(length.start, 16)
        self.assertEqual(length.length, 8)

        dst = mt.get_first_label_with_type(FieldType.Function.DST_ADDRESS)
        self.assertEqual(dst.start, 24)
        self.assertEqual(dst.length, 8)

        seq = mt.get_first_label_with_type(FieldType.Function.SEQUENCE_NUMBER)
        self.assertEqual(seq.start, 32)
        self.assertEqual(seq.length, 8)
