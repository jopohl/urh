import time
from multiprocessing.connection import Pipe

import numpy as np
import unittest

from urh.dev.native.BladeRF import BladeRF
from urh.util import util

util.set_shared_library_path()

from urh.dev.native.lib import bladerf


class TestBladeRF(unittest.TestCase):
    def test_version(self):
        bladerf.get_api_version()

    def test_cython_wrapper(self):
        serials = bladerf.get_device_list()
        print("Connected serials", serials)

        bladerf.open()

        bladerf.set_tx(True)
        bladerf.set_channel(0)
        print("set gain", bladerf.set_gain(20))
        print("set gain", bladerf.set_gain(21))

        bladerf.set_tx(False)
        bladerf.set_channel(1)
        print("Sample Rate", bladerf.get_sample_rate())
        print("Set sample rate to 2e6", bladerf.set_sample_rate(int(2e6)))
        print("sample rate", bladerf.get_sample_rate())
        print("Set sample rate to 40e6", bladerf.set_sample_rate(int(40e6)))
        print("sample rate", bladerf.get_sample_rate())
        print("Set sample rate to 200e6", bladerf.set_sample_rate(int(200e6)))
        print("sample rate", bladerf.get_sample_rate())

        bladerf.set_tx(True)
        bladerf.set_channel(1)
        print("Bandwidth", bladerf.get_bandwidth())
        print("Set Bandwidth to 2e6", bladerf.set_bandwidth(int(2e6)))
        print("Bandwidth", bladerf.get_bandwidth())

        bladerf.set_tx(False)
        bladerf.set_channel(0)
        print("Frequency", bladerf.get_center_freq())
        print("Set Frequency to 433.92e6", bladerf.set_center_freq(int(433.92e6)))
        print("Frequency", bladerf.get_center_freq())

        bladerf.prepare_sync()

        parent_conn, child_conn = Pipe()

        for i in range(3):
            bladerf.receive_sync(child_conn, 4096)
            data = parent_conn.recv_bytes()
            print(data)

        bladerf.close()

        bladerf.open()
        bladerf.set_tx(True)
        bladerf.set_channel(0)
        bladerf.prepare_sync()

        for i in range(10):
            print("Send", bladerf.send_sync(np.fromstring(data, dtype=np.int16)))
        bladerf.close()
