import io
import time
import unittest

import numpy as np
import sys

if sys.platform == "win32":
    import os
    cur_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
    dll_dir = os.path.realpath(os.path.join(cur_dir, "..", "src", "urh", "dev", "native", "lib", "win"))
    os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']


from urh.dev.native.HackRF import HackRF
from urh.dev.native.lib import hackrf


class TestHackRF(unittest.TestCase):
    def callback_fun(self, buffer):
        out = []
        print(buffer)
        for i in range(0, len(buffer), 4):
            try:
                r = np.fromstring(buffer[i:i + 2], dtype=np.float16) / 32767.5
                i = np.fromstring(buffer[i + 2:i + 4], dtype=np.float16) / 32767.5
            except ValueError:
                continue
            if r and i:
                print(r, i)
                # out.append(complex(float(buffer[i:i+1])/32767.5, float(buffer[i+2:i+3])/32767.5))

        return 0

    def test_fromstring(self):
        buffer = b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xff\xfd\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xfe\xfd\xfe\xff\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xfe'
        r = np.empty(len(buffer) // 2, dtype=np.float32)
        i = np.empty(len(buffer) // 2, dtype=np.float32)
        c = np.empty(len(buffer) // 2, dtype=np.complex64)

        # dtype  =
        unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
        ru = unpacked['r'] / 128.0
        iu = unpacked['i'] / 128.0

        # for j in range(0, len(buffer)-1, 2):
        #    r[j//2] = np.frombuffer(buffer[j:j + 1], dtype=np.int8) / 128.0
        #    i[j//2] = np.frombuffer(buffer[j + 1:j + 2], dtype=np.int8) / 128.0
        # r2 = np.fromstring(buffer[], dtype=np.float16) / 32767.5
        c.real = ru
        c.imag = iu
        print(c)
        # x,y = np.frombuffer(buffer, dtype=[('x', np.float16), ('y', np.float16)])

    def test_fromstring2(self):
        buffer = b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xff\xfd\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xfe\xfd\xfe\xff\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfd\xfe'
        c = np.empty(len(buffer) // 2, dtype=np.complex64)

        # dtype  =
        unpacked = np.frombuffer(buffer, dtype="<h") # cast in short
        print(unpacked)
        f = 1.0/32767.5
        for i in range(0, len(unpacked)-1,2):
            c[i] = complex(float(unpacked[i]*f), float(unpacked[i+1]*f))

        print(c)
        # x,y = np.frombuffer(buffer, dtype=[('x', np.float16), ('y', np.float16)])

    def test_hackrf_class_recv(self):
        hfc = HackRF(433.92e6, 1e6, 1e6, 20)
        hfc.start_rx_mode()
        i = 0
        TIME_TOTAL = 5
        while i <TIME_TOTAL:
            print("{0}/{1}".format(i+1, TIME_TOTAL))
            time.sleep(1)
            i+=1
        print("{0:,}".format(hfc.current_recv_index))
        hfc.received_data.tofile("/tmp/hackrf.complex")
        print("Wrote Data")
        hfc.stop_rx_mode("Finished test")

    def test_hackrf_class_send(self):
        hfc = HackRF(433.92e6, 1e6, 1e6, 20)
        hfc.start_tx_mode(np.fromfile("/tmp/hackrf.complex", dtype=np.complex64), repeats=1)
        while not hfc.sending_finished:
            print("Repeat: {0} Current Sample: {1}/{2}".format(hfc.current_sending_repeat+1,
                                                               hfc.current_sent_sample,
                                                               len(hfc.samples_to_send)))
            time.sleep(1)
        hfc.stop_tx_mode("Test finished")

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


if __name__ == "__main__":
    unittest.main()
