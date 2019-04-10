from urh.awre.CommonRange import ChecksumRange
from urh.awre.engines.ChecksumEngine import ChecksumEngine
from urh.util import util
import numpy as np

from tests.awre.AWRETestCase import AWRETestCase


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

        self.assertEqual(checksum_range.message_indices, {0,1,2})