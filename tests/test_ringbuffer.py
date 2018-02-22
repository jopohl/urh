import unittest

import numpy as np

from urh.util.RingBuffer import RingBuffer


class TestRingBuffer(unittest.TestCase):
    def test_push(self):
        ring_buffer = RingBuffer(size=10)
        self.assertEqual(0, ring_buffer.left_index)

        add1 = np.array([1, 2, 3, 4, 5], dtype=np.complex64)
        ring_buffer.push(add1)
        self.assertEqual(5, ring_buffer.right_index)
        self.assertTrue(np.array_equal(ring_buffer.data[0:5], add1))

        add2 = np.array([10, 20, 30, 40, 50, 60], dtype=np.complex64)
        self.assertFalse(ring_buffer.will_fit(len(add2)))
        ring_buffer.push(add2[:-1])
        self.assertTrue(np.array_equal(ring_buffer.data[5:10], add2[:-1]))
        self.assertTrue(np.array_equal(ring_buffer.data[0:5], add1))

    def test_pop(self):
        ring_buffer = RingBuffer(size=5)
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
        popped_item = ring_buffer.pop(1)
        self.assertTrue(np.array_equal(add3[0:1], popped_item), msg=popped_item)
        self.assertFalse(ring_buffer.is_empty)

        add4 = np.array([7, 8, 9, 10], dtype=np.complex64)
        ring_buffer.push(add4)
        self.assertFalse(ring_buffer.will_fit(1))
        self.assertTrue(np.array_equal(np.concatenate((np.atleast_1d(add3[1]), add4)), ring_buffer.pop(5)))

    def test_continuous_pop(self):
        ring_buffer = RingBuffer(size=10)
        values = np.array(list(range(10)), dtype=np.complex64)
        ring_buffer.push(values)
        retrieved = np.array([], dtype=np.complex64)

        for i in range(10):
            retrieved = np.append(retrieved, ring_buffer.pop(1))

        self.assertTrue(np.array_equal(values, retrieved))

    def test_big_buffer(self):
        ring_buffer = RingBuffer(size=5)
        try:
            ring_buffer.push(np.array([1, 2, 3, 4, 5, 6, 7], dtype=np.complex64))
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_will_fit(self):
        ring_buffer = RingBuffer(size=8)
        self.assertEqual(ring_buffer.space_left, 8)
        self.assertTrue(ring_buffer.will_fit(4))
        self.assertTrue(ring_buffer.will_fit(8))
        self.assertFalse(ring_buffer.will_fit(9))
        ring_buffer.push(np.array([1, 2, 3, 4], dtype=np.complex64))
        self.assertEqual(ring_buffer.space_left, 4)
        self.assertTrue(ring_buffer.will_fit(3))
        self.assertTrue(ring_buffer.will_fit(4))
        self.assertFalse(ring_buffer.will_fit(5))


if __name__ == '__main__':
    unittest.main()
