import unittest

import sys

from urh.cythonext.hackrf import HackRF

class TestHackRF(unittest.TestCase):
    def callback_fun(self, hackrf_transfer):
        f = open("/tmp/test.test", "w")
        # array_type = (ctypes.c_byte * length)
        # values = ctypes.cast(hackrf_transfer.contents.buffer, ctypes.POINTER(array_type)).contents
        # # iq data here
        # iq = hackrf.packed_bytes_to_iq(values)
        print("jkefjknskf")
        f.write("klxegmkdrgmkdr")
        return 0


    def test_set_rx(self):
        hackrf = HackRF()
        hackrf.setup()
        hackrf.set_freq(433.92e6)
        hackrf.start_rx_mode(self.callback_fun)
        hackrf.stop_rx_mode()