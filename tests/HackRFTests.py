import io
import time
import unittest

import numpy as np

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

    def test_set_rx(self):
        hackrf.setup()
        hackrf.set_freq(433.92e6)
        print(hackrf.is_streaming())
        hackrf.start_rx_mode(self.callback_fun)
        time.sleep(1)
        hackrf.stop_rx_mode()

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
        hfc = HackRF(1e6, 433.92e6, 20, 1e6)
        hfc.open()
        hfc.start_rx_mode()
        i = 0
        TIME_TOTAL = 5
        while i <TIME_TOTAL:
            print("{0}/{1}".format(i+1, TIME_TOTAL))
            time.sleep(1)
            i+=1
        print("{0:,}".format(hfc.current_recv_index))
        #print(hfc.received_data)
        #hfc.unpack_complex(len(hfc.byte_buffer)//2).tofile("/tmp/hackrf.complex")
        hfc.received_data.tofile("/tmp/hackrf.complex")
        print("Wrote Data")
        hfc.stop_rx_mode("Finished test")
        hfc.close()

    def test_hackrf_class_send(self):
        hfc = HackRF(1e6, 433.92e6, 20, 1e6)
        hfc.open()
        hfc.start_tx_mode(np.fromfile("/tmp/hackrf.complex",dtype=np.complex64), repeats=10)
        while not hfc.sending_finished:
            print("Repeat: {0} Current Sample: {1}".format(hfc.current_sending_repeat+1, hfc.current_sent_sample))
            time.sleep(1)
        hfc.stop_tx_mode("Test finished")
        hfc.close()

    def test_hackrf_class_send_recv(self):
        while True:
            t = time.time()
            hfc = HackRF(1e6, 433.92e6, 20, 1e6)
            hfc.open()
            print("opening time:", time.time()-t)
            hfc.start_rx_mode()
            i = 0
            t = time.time()
            while i < 1:
                #print("{0}/{1}".format(i+1, 5))
                time.sleep(1)
                i+=1
            print("{0:,}".format(hfc.current_recv_index))
            rcv_data = hfc.received_data
            print("Rcv done {0}".format(time.time()-t))

            t = time.time()
            hfc.stop_rx_mode("Finished test")
            #hfc.reopen()
            #print("reopen", 1000*(time.time()-t))
            #hfc.close()
            hfc.open()
            hfc.start_tx_mode(rcv_data, repeats=1)
            print("             Switch time:", 1000*(time.time()-t), "ms")
            t = time.time()
            while not hfc.sending_finished:
                #print("Repeat: {0} Current Sample: {1}".format(hfc.current_sending_repeat + 1, hfc.current_sent_sample))
                time.sleep(0.01)
            print("Send time", time.time()-t)
            t = time.time()
            hfc.stop_tx_mode("Test finished")
            #hfc.close()
            print("Close time", time.time()-t)

    def test_lookup(self):
        # https://github.com/osmocom/gr-osmosdr/blob/master/lib/hackrf/hackrf_source_c.cc#L127
        lookup = np.empty(0xffff, dtype=np.complex64)
        for i in range(0, 0xffff):
            real = float(np.uint8(i >> 8)) * 1 / 128
            imag = float(np.uint8(i & 0xff)) * 1 / 128
            lookup[i] = complex(real, imag)

        buffer = b"\x00\x01"
        unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
        ru = unpacked['r'] / 128.0
        iu = unpacked['i'] / 128.0

        # seems to be the same

        # Convert floated again???
        # https://github.com/osmocom/gr-osmosdr/blob/master/lib/osmosdr/osmosdr_src_c.cc#L235

        print(lookup[0x0001])
        print(ru, iu)


    def test_pack_complex(self):
        hkrf = HackRF(1,1,1,1)
        print(hkrf.pack_complex(np.array([complex(0.1, 0.1), complex(0.5, 0.1)], dtype=np.complex64)))

    def test_buffer_io(self):
        b = io.BytesIO(b"\x00\x01\x02\x03\x04\x05\x06")
        br = io.BufferedReader(b) # Buffered Reader is thread safe https://docs.python.org/3/library/io.html#multi-threading
        print(bool(br.peek()))
        print(br.read(2))
        print(br.tell())
        print(br.read(2))
        print(br.read(2))
        print(br.read(2))
        br.seek(0)
        print(br.read1(2))
        print(br.tell())
        print(bool(br.peek()))
        br.close()
        b.close()
        br.close()