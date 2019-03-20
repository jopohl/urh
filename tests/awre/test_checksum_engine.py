from urh.awre.engines.ChecksumEngine import ChecksumEngine
from urh.util import util
import numpy as np

from tests.awre.AWRETestCase import AWRETestCase


class TestChecksumEngine(AWRETestCase):
    def test_find_crc8(self):
        messages = ["aabbcc7d", "abcdee24", "dacafe33"]
        message_bits = [np.array(msg, dtype=np.uint8) for msg in map(util.hex2bit, messages)]

        checksum_engine = ChecksumEngine(message_bits, n_gram_length=8)
        print(checksum_engine.find())
