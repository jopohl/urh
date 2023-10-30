import unittest

import numpy as np

from urh.signalprocessing.IQArray import IQArray


class TestIQArray(unittest.TestCase):
    def test_index(self):
        iq_array = IQArray(np.array([1, 2, 3, 4, 5, 6], dtype=np.uint8))

        self.assertEqual(iq_array[0][0], 1)
        self.assertEqual(iq_array[0][1], 2)

        self.assertEqual(iq_array[1][0], 3)
        self.assertEqual(iq_array[1][1], 4)

        self.assertEqual(iq_array[2][0], 5)
        self.assertEqual(iq_array[2][1], 6)

        self.assertEqual(iq_array[1:2][0, 0], 3)
        self.assertEqual(iq_array[1:2][0, 1], 4)

        self.assertEqual(iq_array[:2][0, 0], 1)
        self.assertEqual(iq_array[:2][0, 1], 2)
        self.assertEqual(iq_array[:2][1, 0], 3)
        self.assertEqual(iq_array[:2][1, 1], 4)

        iq_array[0] = np.array([13, 37])
        self.assertEqual(iq_array[0][0], 13)
        self.assertEqual(iq_array[0][1], 37)

        iq_array[0:2] = np.array([42, 42, 47, 11])
        self.assertEqual(iq_array[0][0], 42)
        self.assertEqual(iq_array[0][1], 42)
        self.assertEqual(iq_array[1][0], 47)
        self.assertEqual(iq_array[1][1], 11)

    def test_conversion_iq16s(self):
        iq16s = IQArray(np.array([-128, 0, 0, 127], dtype=np.int8))
        self.assertTrue(
            np.array_equal(
                iq16s.convert_to(np.int8).flatten(),
                np.array([-128, 0, 0, 127], dtype=np.int8),
            )
        )
        self.assertTrue(
            np.array_equal(
                iq16s.convert_to(np.uint8).flatten(),
                np.array([0, 128, 128, 255], dtype=np.uint8),
            )
        )

        c32s = iq16s.convert_to(np.int16).flatten()
        self.assertTrue(
            np.array_equal(c32s, np.array([-32768, 0, 0, 32512], dtype=np.int16)),
            msg=c32s,
        )

        c32u = iq16s.convert_to(np.uint16).flatten()
        self.assertTrue(
            np.array_equal(c32u, np.array([0, 32768, 32768, 65280], dtype=np.uint16)),
            msg=c32u,
        )

        c64f = iq16s.convert_to(np.float32).flatten()
        self.assertTrue(
            np.array_equal(c64f, np.array([-1, 0, 0, 0.9921875], dtype=np.float32)),
            msg=c64f,
        )

    def test_conversion_iq16u(self):
        iq16u = IQArray(np.array([0, 128, 128, 255], dtype=np.uint8))
        self.assertTrue(
            np.array_equal(
                iq16u.convert_to(np.uint8).flatten(),
                np.array([0, 128, 128, 255], dtype=np.uint8),
            )
        )
        iq16s = iq16u.convert_to(np.int8).flatten()
        self.assertTrue(
            np.array_equal(iq16s, np.array([-128, 0, 0, 127], dtype=np.int8)), msg=iq16s
        )

        c32s = iq16u.convert_to(np.int16).flatten()
        self.assertTrue(
            np.array_equal(c32s, np.array([-32768, 0, 0, 32512], dtype=np.int16)),
            msg=c32s,
        )

        c32u = iq16u.convert_to(np.uint16).flatten()
        self.assertTrue(
            np.array_equal(c32u, np.array([0, 32768, 32768, 65280], dtype=np.uint16)),
            msg=c32u,
        )

        c64f = iq16u.convert_to(np.float32).flatten()
        self.assertTrue(
            np.array_equal(c64f, np.array([-1, 0, 0, 0.9921875], dtype=np.float32)),
            msg=c64f,
        )

    def test_conversion_iq32s(self):
        iq32s = IQArray(np.array([-32768, 0, 0, 32767], dtype=np.int16))
        self.assertTrue(
            np.array_equal(
                iq32s.convert_to(np.int16).flatten(),
                np.array([-32768, 0, 0, 32767], dtype=np.int16),
            )
        )

        iq32u = iq32s.convert_to(np.uint16).flatten()
        self.assertTrue(
            np.array_equal(iq32u, np.array([0, 32768, 32768, 65535], dtype=np.uint16)),
            msg=iq32u,
        )

        iq16s = iq32s.convert_to(np.int8).flatten()
        self.assertTrue(
            np.array_equal(iq16s, np.array([-128, 0, 0, 127], dtype=np.int8)), msg=iq16s
        )

        iq16u = iq32s.convert_to(np.uint8).flatten()
        self.assertTrue(
            np.array_equal(iq16u, np.array([0, 128, 128, 255], dtype=np.uint8)),
            msg=iq16u,
        )

        iq64f = iq32s.convert_to(np.float32).flatten()
        self.assertTrue(
            np.array_equal(iq64f, np.array([-1, 0, 0, 0.9999695], dtype=np.float32)),
            msg=iq64f,
        )

    def test_conversion_iq32u(self):
        iq32u = IQArray(np.array([0, 32768, 32768, 65535], dtype=np.uint16))
        self.assertTrue(
            np.array_equal(
                iq32u.convert_to(np.uint16).flatten(),
                np.array([0, 32768, 32768, 65535], dtype=np.uint16),
            )
        )

        iq32s = iq32u.convert_to(np.int16).flatten()
        self.assertTrue(
            np.array_equal(iq32s, np.array([-32768, 0, 0, 32767], dtype=np.int16)),
            msg=iq32s,
        )

        iq16s = iq32u.convert_to(np.int8).flatten()
        self.assertTrue(
            np.array_equal(iq16s, np.array([-128, 0, 0, 127], dtype=np.int8)), msg=iq16s
        )

        iq16u = iq32u.convert_to(np.uint8).flatten()
        self.assertTrue(
            np.array_equal(iq16u, np.array([0, 128, 128, 255], dtype=np.uint8)),
            msg=iq16u,
        )

        iq64f = iq32u.convert_to(np.float32).flatten()
        self.assertTrue(
            np.array_equal(iq64f, np.array([-1, 0, 0, 0.9999695], dtype=np.float32)),
            msg=iq64f,
        )

    def test_conversion_iq64f(self):
        iq64f = IQArray(np.array([-1, 0, 0, 1], dtype=np.float32))
        self.assertTrue(
            np.array_equal(
                iq64f.convert_to(np.float32).flatten(),
                np.array([-1, 0, 0, 1], dtype=np.float32),
            )
        )

        iq16u = iq64f.convert_to(np.uint8).flatten()
        self.assertTrue(
            np.array_equal(iq16u, np.array([0, 127, 127, 254], dtype=np.uint8)),
            msg=iq16u,
        )

        iq16s = iq64f.convert_to(np.int8).flatten()
        self.assertTrue(
            np.array_equal(iq16s, np.array([-127, 0, 0, 127], dtype=np.int8)), msg=iq16s
        )

        iq32s = iq64f.convert_to(np.int16).flatten()
        self.assertTrue(
            np.array_equal(iq32s, np.array([-32767, 0, 0, 32767], dtype=np.int16)),
            msg=iq32s,
        )

        iq32u = iq64f.convert_to(np.uint16).flatten()
        self.assertTrue(
            np.array_equal(iq32u, np.array([0, 32767, 32767, 65534], dtype=np.uint16)),
            msg=iq32u,
        )
