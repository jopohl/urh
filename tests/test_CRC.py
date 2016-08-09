import unittest

from urh.signalprocessing.encoding import encoding
from urh.util.crc import crc_generic

class TestCRC(unittest.TestCase):
    # Testmethode muss immer mit Präfix test_* starten
    def test_crc(self):
        c = crc_generic(polynomial="8_en")
        e = encoding()

        str = ["aad3d5ddddcc5d45ddbba", "aad4ddddddcc5d45ddbca", "aad3c5ddddcc5d45ddbaa", "aad4ddddddcc5d45ddbca"]

        for v in str:
            print(v, e.bit2hex(c.crc(e.hex2bit(v[1:-2]))))
            print(c.guess_standard_parameters(e.hex2bit(v[1:-2]), e.hex2bit(v[-2:])))



