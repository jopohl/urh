import unittest

import sys

import time
import numpy as np

from urh.cythonext import hackrf
from urh.dev.HackRF import HackRF


class TestHackRF(unittest.TestCase):
    def callback_fun(self, buffer):
        out = []
        print(buffer)
        for i in range(0,len(buffer), 4):
            try:
                r = np.fromstring(buffer[i:i+2], dtype=np.float16)/32767.5
                i = np.fromstring(buffer[i+2:i+4], dtype=np.float16)/32767.5
            except ValueError:
                continue
            if r and i:
                print(r,i)
            #out.append(complex(float(buffer[i:i+1])/32767.5, float(buffer[i+2:i+3])/32767.5))

        return 0


    def test_set_rx(self):
        hackrf.setup()
        hackrf.set_freq(433.92e6)
        print(hackrf.is_streaming())
        hackrf.start_rx_mode(self.callback_fun)
        time.sleep(1)
        hackrf.stop_rx_mode()

    def test_fromstring(self):
        buffer = b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xff\xfd\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xfe\xfd\xfe\xff\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xfe'
        r = np.empty(len(buffer)//2, dtype=np.float32)
        i = np.empty(len(buffer)//2, dtype=np.float32)
        c = np.empty(len(buffer)//2, dtype=np.complex64)

        #dtype  =
        unpacked = np.frombuffer(buffer, dtype=[('r', np.int8), ('i', np.int8)])
        ru = unpacked['r'] / 128.0
        iu = unpacked['i'] / 128.0

        #for j in range(0, len(buffer)-1, 2):
        #    r[j//2] = np.frombuffer(buffer[j:j + 1], dtype=np.int8) / 128.0
        #    i[j//2] = np.frombuffer(buffer[j + 1:j + 2], dtype=np.int8) / 128.0
        #r2 = np.fromstring(buffer[], dtype=np.float16) / 32767.5
        c.real = ru
        c.imag = iu
        print(c)
        #x,y = np.frombuffer(buffer, dtype=[('x', np.float16), ('y', np.float16)])


    def test_hackrf_class(self):
        hfc = HackRF(1e6, 433e6, 20, 1e6)
        hfc.open()
        hfc.start_rx_mode()
        time.sleep(5)
        print(hfc.current_index)
        print(hfc.received_data)
        hfc.stop_rx_mode("Finished test")
        #hfc.close()