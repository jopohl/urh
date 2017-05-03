import unittest

import numpy as np

from urh.util.RingBuffer import RingBuffer


class TestRingBuffer(unittest.TestCase):
    def test_push(self):
        ring_buffer = RingBuffer(size=10, dtype=np.complex64)
        self.assertFalse(ring_buffer.is_full)
        self.assertEqual(0, ring_buffer.current_index)

        add1 = np.array([1, 2, 3, 4, 5], dtype=np.complex64)
        ring_buffer.push(add1)
        self.assertEqual(5, ring_buffer.current_index)
        self.assertFalse(ring_buffer.is_full)
        self.assertTrue(np.array_equal(ring_buffer[0:5], add1))

        add2 = np.array([10, 20, 30, 40, 50, 60], dtype=np.complex64)
        ring_buffer.push(add2)
        self.assertTrue(ring_buffer.is_full)
        self.assertTrue(np.array_equal(ring_buffer[0:6], add2))
        self.assertTrue(np.array_equal(ring_buffer[6:10], add1[:-1]))

    def test_pop(self):
        ring_buffer = RingBuffer(size=5, dtype=np.complex64)
        add1 = np.array([1, 2, 3], dtype=np.complex64)
        ring_buffer.push(add1)
        self.assertTrue(np.array_equal(add1, ring_buffer.pop(40)))
        self.assertTrue(ring_buffer.is_empty)

        add2 = np.array([1, 2, 3, 4], dtype=np.complex64)
        ring_buffer.push(add2)
        self.assertTrue(np.array_equal(add2, ring_buffer.pop(4)))
        self.assertTrue(ring_buffer.is_empty)

        add3 = np.array([1, 2], dtype=np.complex64)
        ring_buffer.push(add3)
        self.assertTrue(np.array_equal(add3[1:], ring_buffer.pop(1)))
        self.assertFalse(ring_buffer.is_empty)

    def test_big_buffer(self):
        ring_buffer = RingBuffer(size=5, dtype=np.complex64)
        try:
            ring_buffer.push(np.array([1, 2, 3, 4, 5, 6, 7], dtype=np.complex64))
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_will_fit(self):
        ring_buffer = RingBuffer(size=8, dtype=np.complex64)
        self.assertTrue(ring_buffer.will_fit(4))
        self.assertTrue(ring_buffer.will_fit(8))
        self.assertFalse(ring_buffer.will_fit(9))
        ring_buffer.push(np.array([1, 2, 3, 4], dtype=np.complex64))
        self.assertTrue(ring_buffer.will_fit(3))
        self.assertTrue(ring_buffer.will_fit(4))
        self.assertFalse(ring_buffer.will_fit(5))

if __name__ == '__main__':
    unittest.main()
