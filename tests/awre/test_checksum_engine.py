import array

import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.CommonRange import ChecksumRange
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.ChecksumEngine import ChecksumEngine
from urh.signalprocessing.FieldType import FieldType
from urh.util import util
from urh.util.GenericCRC import GenericCRC
from urh.cythonext import util as c_util


class TestChecksumEngine(AWRETestCase):
    def test_find_crc8(self):
        messages = ["aabbcc7d", "abcdee24", "dacafe33"]
        message_bits = [
            np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)
        ]

        checksum_engine = ChecksumEngine(message_bits, n_gram_length=8)
        result = checksum_engine.find()
        self.assertEqual(len(result), 1)
        checksum_range = result[0]  # type: ChecksumRange
        self.assertEqual(checksum_range.length, 8)
        self.assertEqual(checksum_range.start, 24)

        reference = GenericCRC()
        reference.set_polynomial_from_hex("0x07")
        self.assertEqual(checksum_range.crc.polynomial, reference.polynomial)

        self.assertEqual(checksum_range.message_indices, {0, 1, 2})

    def test_find_crc16(self):
        messages = ["12345678347B", "abcdefffABBD", "cafe1337CE12"]
        message_bits = [
            np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)
        ]

        checksum_engine = ChecksumEngine(message_bits, n_gram_length=8)
        result = checksum_engine.find()
        self.assertEqual(len(result), 1)
        checksum_range = result[0]  # type: ChecksumRange
        self.assertEqual(checksum_range.start, 32)
        self.assertEqual(checksum_range.length, 16)

        reference = GenericCRC()
        reference.set_polynomial_from_hex("0x8005")
        self.assertEqual(checksum_range.crc.polynomial, reference.polynomial)

        self.assertEqual(checksum_range.message_indices, {0, 1, 2})

    def test_find_crc32(self):
        messages = ["deadcafe5D7F3F5A", "47111337E3319242", "beefaffe0DCD0E15"]
        message_bits = [
            np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)
        ]

        checksum_engine = ChecksumEngine(message_bits, n_gram_length=8)
        result = checksum_engine.find()
        self.assertEqual(len(result), 1)
        checksum_range = result[0]  # type: ChecksumRange
        self.assertEqual(checksum_range.start, 32)
        self.assertEqual(checksum_range.length, 32)

        reference = GenericCRC()
        reference.set_polynomial_from_hex("0x04C11DB7")
        self.assertEqual(checksum_range.crc.polynomial, reference.polynomial)

        self.assertEqual(checksum_range.message_indices, {0, 1, 2})

    def test_find_generated_crc16(self):
        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.DATA, 32)
        mb.add_checksum_label(16, GenericCRC.from_standard_checksum("CRC16 CCITT"))

        mb2 = MessageTypeBuilder("data2")
        mb2.add_label(FieldType.Function.PREAMBLE, 8)
        mb2.add_label(FieldType.Function.SYNC, 16)
        mb2.add_label(FieldType.Function.LENGTH, 8)
        mb2.add_label(FieldType.Function.DATA, 16)

        mb2.add_checksum_label(16, GenericCRC.from_standard_checksum("CRC16 CCITT"))

        pg = ProtocolGenerator(
            [mb.message_type, mb2.message_type],
            syncs_by_mt={mb.message_type: "0x1234", mb2.message_type: "0x1234"},
        )

        num_messages = 5

        for i in range(num_messages):
            pg.generate_message(data="{0:032b}".format(i), message_type=mb.message_type)
            pg.generate_message(
                data="{0:016b}".format(i), message_type=mb2.message_type
            )

        # self.save_protocol("crc16_test", pg)
        self.clear_message_types(pg.protocol.messages)

        ff = FormatFinder(pg.protocol.messages)
        ff.run()

        self.assertEqual(len(ff.message_types), 2)
        for mt in ff.message_types:
            checksum_label = mt.get_first_label_with_type(FieldType.Function.CHECKSUM)
            self.assertEqual(checksum_label.length, 16)
            self.assertEqual(checksum_label.checksum.caption, "CRC16 CCITT")
