from tests.awre.AWRETestCase import AWRETestCase
from urh.awre import AutoAssigner
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant
from urh.util import util


class TestGeneratedProtocols(AWRETestCase):
    def __check_addresses(self, messages, format_finder, known_participant_addresses):
        """
        Use the AutoAssigner used also in main GUI to test assigned participant addresses to get same results
        as in main program and not rely on cache of FormatFinder, because values there might be false
        but SRC address labels still on right position which is the basis for Auto Assigner

        :param messages:
        :param format_finder:
        :param known_participant_addresses:
        :return:
        """

        for msg_type, indices in format_finder.existing_message_types.items():
            for i in indices:
                messages[i].message_type = msg_type

        participants = list(set(m.participant for m in messages))
        for p in participants:
            p.address_hex = ""
        AutoAssigner.auto_assign_participant_addresses(messages, participants)

        for i in range(len(participants)):
            self.assertIn(
                participants[i].address_hex,
                list(
                    map(
                        util.convert_numbers_to_hex_string,
                        known_participant_addresses.values(),
                    )
                ),
                msg=" [ " + " ".join(p.address_hex for p in participants) + " ]",
            )

    def test_without_preamble(self):
        alice = Participant("Alice", address_hex="24")
        broadcast = Participant("Broadcast", address_hex="ff")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x8e88"},
            preambles_by_mt={mb.message_type: "10" * 8},
            participants=[alice, broadcast],
        )

        for i in range(20):
            data_bits = 16 if i % 2 == 0 else 32
            source = pg.participants[i % 2]
            destination = pg.participants[(i + 1) % 2]
            pg.generate_message(
                data="1010" * (data_bits // 4), source=source, destination=destination
            )

        # self.save_protocol("without_preamble", pg)
        self.clear_message_types(pg.messages)
        ff = FormatFinder(pg.messages)
        ff.known_participant_addresses.clear()

        ff.run()
        self.assertEqual(len(ff.message_types), 1)

        mt = ff.message_types[0]
        sync = mt.get_first_label_with_type(FieldType.Function.SYNC)
        self.assertEqual(sync.start, 0)
        self.assertEqual(sync.length, 16)

        length = mt.get_first_label_with_type(FieldType.Function.LENGTH)
        self.assertEqual(length.start, 16)
        self.assertEqual(length.length, 8)

        dst = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        self.assertEqual(dst.start, 24)
        self.assertEqual(dst.length, 8)

        seq = mt.get_first_label_with_type(FieldType.Function.SEQUENCE_NUMBER)
        self.assertEqual(seq.start, 32)
        self.assertEqual(seq.length, 8)

    def test_without_preamble_random_data(self):
        ff = self.get_format_finder_from_protocol_file(
            "without_ack_random_data.proto.xml"
        )
        ff.run()

        self.assertEqual(len(ff.message_types), 1)

        mt = ff.message_types[0]
        sync = mt.get_first_label_with_type(FieldType.Function.SYNC)
        self.assertEqual(sync.start, 0)
        self.assertEqual(sync.length, 16)

        length = mt.get_first_label_with_type(FieldType.Function.LENGTH)
        self.assertEqual(length.start, 16)
        self.assertEqual(length.length, 8)

        dst = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        self.assertEqual(dst.start, 24)
        self.assertEqual(dst.length, 8)

        seq = mt.get_first_label_with_type(FieldType.Function.SEQUENCE_NUMBER)
        self.assertEqual(seq.start, 32)
        self.assertEqual(seq.length, 8)

    def test_without_preamble_random_data2(self):
        ff = self.get_format_finder_from_protocol_file(
            "without_ack_random_data2.proto.xml"
        )
        ff.run()

        self.assertEqual(len(ff.message_types), 1)

        mt = ff.message_types[0]
        sync = mt.get_first_label_with_type(FieldType.Function.SYNC)
        self.assertEqual(sync.start, 0)
        self.assertEqual(sync.length, 16)

        length = mt.get_first_label_with_type(FieldType.Function.LENGTH)
        self.assertEqual(length.start, 16)
        self.assertEqual(length.length, 8)

        dst = mt.get_first_label_with_type(FieldType.Function.SRC_ADDRESS)
        self.assertEqual(dst.start, 24)
        self.assertEqual(dst.length, 8)

        seq = mt.get_first_label_with_type(FieldType.Function.SEQUENCE_NUMBER)
        self.assertEqual(seq.start, 32)
        self.assertEqual(seq.length, 8)

    def test_with_checksum(self):
        ff = self.get_format_finder_from_protocol_file(
            "with_checksum.proto.xml", clear_participant_addresses=False
        )
        known_participant_addresses = ff.known_participant_addresses.copy()
        ff.known_participant_addresses.clear()
        ff.run()

        self.assertIn(
            known_participant_addresses[0].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )
        self.assertIn(
            known_participant_addresses[1].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )

        self.assertEqual(len(ff.message_types), 3)

    def test_with_only_one_address(self):
        ff = self.get_format_finder_from_protocol_file(
            "only_one_address.proto.xml", clear_participant_addresses=False
        )
        known_participant_addresses = ff.known_participant_addresses.copy()
        ff.known_participant_addresses.clear()

        ff.run()

        self.assertIn(
            known_participant_addresses[0].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )
        self.assertIn(
            known_participant_addresses[1].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )

    def test_with_four_broken(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "four_broken.proto.xml",
            clear_participant_addresses=False,
            return_messages=True,
        )

        assert isinstance(ff, FormatFinder)
        known_participant_addresses = ff.known_participant_addresses.copy()
        ff.known_participant_addresses.clear()

        ff.run()

        self.__check_addresses(messages, ff, known_participant_addresses)

        for i in range(4, len(messages)):
            mt = next(
                mt for mt, indices in ff.existing_message_types.items() if i in indices
            )
            self.assertIsNotNone(
                mt.get_first_label_with_type(FieldType.Function.SEQUENCE_NUMBER)
            )

    def test_with_one_address_one_message_type(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "one_address_one_mt.proto.xml",
            clear_participant_addresses=False,
            return_messages=True,
        )

        self.assertEqual(len(messages), 17)
        self.assertEqual(len(ff.hexvectors), 17)

        known_participant_addresses = ff.known_participant_addresses.copy()
        ff.known_participant_addresses.clear()

        ff.run()

        self.assertEqual(len(ff.message_types), 1)

        self.assertIn(
            known_participant_addresses[0].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )
        self.assertIn(
            known_participant_addresses[1].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )

    def test_without_preamble_24_messages(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "no_preamble24.proto.xml",
            clear_participant_addresses=False,
            return_messages=True,
        )

        known_participant_addresses = ff.known_participant_addresses.copy()
        ff.known_participant_addresses.clear()

        ff.run()

        self.assertEqual(len(ff.message_types), 1)

        self.assertIn(
            known_participant_addresses[0].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )
        self.assertIn(
            known_participant_addresses[1].tostring(),
            list(map(bytes, ff.known_participant_addresses.values())),
        )

    def test_with_three_syncs_different_preamble_lengths(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "three_syncs.proto.xml", return_messages=True
        )
        preprocessor = Preprocessor(ff.get_bitvectors_from_messages(messages))
        sync_words = preprocessor.find_possible_syncs()
        self.assertIn("0000010000100000", sync_words, msg="Sync 1")
        self.assertIn("0010001000100010", sync_words, msg="Sync 2")
        self.assertIn("0110011101100111", sync_words, msg="Sync 3")

        ff.run()

        expected_sync_ends = [
            32,
            24,
            40,
            24,
            32,
            24,
            40,
            24,
            32,
            24,
            40,
            24,
            32,
            24,
            40,
            24,
        ]

        for i, (s1, s2) in enumerate(zip(expected_sync_ends, ff.sync_ends)):
            self.assertEqual(s1, s2, msg=str(i))

    def test_with_four_participants(self):
        ff, messages = self.get_format_finder_from_protocol_file(
            "four_participants.proto.xml",
            clear_participant_addresses=False,
            return_messages=True,
        )

        known_participant_addresses = ff.known_participant_addresses.copy()
        ff.known_participant_addresses.clear()

        ff.run()

        self.__check_addresses(messages, ff, known_participant_addresses)
        self.assertEqual(len(ff.message_types), 3)
