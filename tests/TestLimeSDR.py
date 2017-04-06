import unittest
import sys

import numpy as np
from multiprocessing import Pipe

if sys.platform == "win32":
    import os

    cur_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
    dll_dir = os.path.realpath(os.path.join(cur_dir, "..", "src", "urh", "dev", "native", "lib", "win"))
    os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']

from urh.dev.native.lib import limesdr


class TestLimeSDR(unittest.TestCase):
    def test_cython_wrapper(self):
        print("Devices:", limesdr.get_device_list())
        # print("Open:", limesdr.open("LimeSDR-USB, media=USB 3.0, module=STREAM, addr=1d50:6108, serial=0009060B0049180A"))
        print("Open:", limesdr.open())
        print("-" * 20)

        print("Is Open 0:", limesdr.is_open(0))
        print("Is Open 1:", limesdr.is_open(1))
        print("Init", limesdr.init())
        print("Num Channels TX:", limesdr.get_num_channels(True))
        print("Num Channels RX:", limesdr.get_num_channels(False))
        print("Enable RX Channel 0:", limesdr.enable_channel(dir_tx=False, chan=0, enabled=True))

        print("RX Sample Rate Range:", limesdr.get_sample_rate_range(False))
        print("RX Channel 0 Sample Rate:", limesdr.get_sample_rate(dir_tx=False, chan=0))
        print("Set Sample Rate:", limesdr.set_sample_rate(2e6, 0))
        print("RX Channel 0 Sample Rate:", limesdr.get_sample_rate(dir_tx=False, chan=0))

        print("RX Frequency Range:", limesdr.get_center_frequency_range(False))
        print("RX 0 center freq:", limesdr.get_center_frequency(False, 0))
        print("RX 0 set center freq:", limesdr.set_center_frequency(False, 0, 433.92e6))
        print("RX 0 center freq:", limesdr.get_center_frequency(False, 0))

        print("RX 0 gain", limesdr.get_normalized_gain(False, 0))
        print("RX 0 set gain", limesdr.set_normalized_gain(False, 0, 0.5))
        print("RX 0 gain", limesdr.get_normalized_gain(False, 0))

        print("RX Bandwidth Range", limesdr.get_lpf_bandwidth_range(False))
        print("RX 0 Bandwidth", limesdr.get_lpf_bandwidth(False, 0))
        print("RX 0 set Bandwidth", limesdr.set_lpf_bandwidth(False, 0, 20e6))
        print("RX 0 Bandwidth", limesdr.get_lpf_bandwidth(False, 0))

        print("RX 0 calibrate:", limesdr.calibrate(False, 0, 20e6))

        antenna_list = limesdr.get_antenna_list(False, 0)
        print("RX 0 antenna list", antenna_list)
        print("RX 0 current antenna", limesdr.get_antenna(False, 0), antenna_list[limesdr.get_antenna(False, 0)])
        print("RX 0 current antenna BW", limesdr.get_antenna_bw(False, 0, limesdr.get_antenna(False, 0)))

        print("Chip Temperature", limesdr.get_chip_temperature())

        parent_conn, child_conn = Pipe()

        for _ in range(2):
            print("Setup stream", limesdr.setup_stream(False, 0, 1000))
            print("Start stream", limesdr.start_stream())
            limesdr.recv_stream(child_conn, 1000, 100)
            print("Stop stream", limesdr.stop_stream())
            print("Destroy stream", limesdr.destroy_stream())

            print(parent_conn.recv_bytes())

        print("-" * 20)
        print("Close:", limesdr.close())
        print("Is Open 0:", limesdr.is_open(0))
        print("Is Open 1:", limesdr.is_open(1))



if __name__ == "__main__":
    unittest.main()
