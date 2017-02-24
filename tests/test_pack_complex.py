import unittest

import numpy as np

from urh.dev.native.HackRF import HackRF


class TestPackComplex(unittest.TestCase):
    def test_hackrf_pack_unpack(self):
        arr = np.array([-128, -128, -0.5, -0.5, -3, -3, 127, 127], dtype=np.int8)
        self.assertEqual(arr[0], -128)
        self.assertEqual(arr[1], -128)
        self.assertEqual(arr[-1], 127)

        received = arr.tostring()
        self.assertEqual(len(received), len(arr))
        self.assertEqual(np.int8(received[0]), -128)
        self.assertEqual(np.int8(received[1]), -128)
        unpacked = HackRF.unpack_complex(received, len(received) // 2)
        self.assertEqual(unpacked[0], complex(-1, -1))
        self.assertAlmostEqual(unpacked[1], complex(0, 0), places=1)
        self.assertAlmostEqual(unpacked[2], complex(0, 0), places=1)
        self.assertEqual(unpacked[3], complex(1, 1))

        packed = HackRF.pack_complex(unpacked)
        self.assertEqual(received, packed)
