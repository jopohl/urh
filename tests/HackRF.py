import unittest

import sys

import time

from urh.cythonext import hackrf

class TestHackRF(unittest.TestCase):
    def callback_fun(self, buffer):
        # array_type = (ctypes.c_byte * length)
        # values = ctypes.cast(hackrf_transfer.contents.buffer, ctypes.POINTER(array_type)).contents
        # # iq data here
        # iq = hackrf.packed_bytes_to_iq(values)
        print(len(buffer))
        return 0


    def test_set_rx(self):
        hackrf.setup()
        hackrf.set_freq(433.92e6)
        print(hackrf.is_streaming())
        hackrf.start_rx_mode(self.callback_fun)
        time.sleep(0.1)
        print(hackrf.is_streaming())
        hackrf.stop_rx_mode()