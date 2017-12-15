import unittest

import time
from multiprocessing.connection import Connection, Pipe

import numpy as np
from multiprocessing import Process

from urh.dev.native.SDRPlay import SDRPlay
from urh.util import util
import ctypes

util.set_windows_lib_path()

from urh.dev.native.lib import sdrplay

def recv(conn: Connection):
    while True:
        t = time.time()
        result = SDRPlay.unpack_complex(conn.recv_bytes())
        print("UNPACK", time.time()-t)

class TestSDRPlay(unittest.TestCase):
    def test_c_wrapper(self):
        def pycallback(data):
            arr = np.asarray(data)
            #result = np.empty(len(arr) // 2, dtype=np.complex64)
            #result.real = (arr[::2] + 0.5) / 32767.5
            #result.imag = (arr[1::2] + 0.5) / 32767.5

        print(sdrplay.get_api_version())
        print(sdrplay.get_devices())
        print(sdrplay.set_device_index(0))

        parent_conn, child_conn = Pipe()
        p = Process(target=recv, args=(parent_conn,))
        p.daemon = True
        p.start()

        null_ptr = ctypes.POINTER(ctypes.c_voidp)()
        print("Init stream", sdrplay.init_stream(50, 2e6, 433.92e6, 2e6, 500, child_conn))

        time.sleep(2)
        print("settings sample rate")
        print("Set sample rate", sdrplay.set_sample_rate(2e6))

        time.sleep(1)
        p.terminate()
        p.join()
