import unittest

import time

from urh.signalprocessing.ContinuousModulator import ContinuousModulator
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator


class TestContinuousModulator(unittest.TestCase):
    NUM_MESSAGES = 20
    BITS_PER_MESSAGE = 100

    def test_modulate_continuously(self):
        modulator = Modulator("Test")
        continuous_modulator = ContinuousModulator(self.__create_messages(), [modulator])

        self.assertEqual(continuous_modulator.current_message_index, 0)
        self.assertTrue(continuous_modulator.ring_buffer.is_empty)
        continuous_modulator.start()
        self.assertTrue(continuous_modulator.thread.is_alive())
        time.sleep(0.1)
        self.assertFalse(continuous_modulator.ring_buffer.is_empty)
        self.assertGreater(continuous_modulator.current_message_index, 0)
        continuous_modulator.stop()
        self.assertFalse(continuous_modulator.thread.is_alive())

    def __create_messages(self):
        mt = MessageType("test")
        return [Message([True] * self.BITS_PER_MESSAGE, 1000, mt) for _ in range(self.NUM_MESSAGES)]

if __name__ == '__main__':
    unittest.main()
