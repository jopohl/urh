import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.CommonRange import ChecksumRange
from urh.awre.engines.ChecksumEngine import ChecksumEngine
from urh.util import util
from urh.util.GenericCRC import GenericCRC


class TestChecksumEngine(AWRETestCase):
    def test_find_crc8(self):
        messages = ["aabbcc7d", "abcdee24", "dacafe33"]
        message_bits = [np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)]

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
        message_bits = [np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)]

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
        message_bits = [np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)]

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
