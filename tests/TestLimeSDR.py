import unittest
import sys

import os
from multiprocessing import Pipe
f = os.readlink(__file__) if os.path.islink(__file__) else __file__
path = os.path.realpath(os.path.join(f, "..", "..", "src"))

if path not in sys.path:
    sys.path.insert(0, path)

import numpy as np

from urh.util import util

util.set_windows_lib_path()

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
        limesdr.set_tx(True)
        self.assertTrue(limesdr.get_tx())
        #print(limesdr.IS_TX)
        print("Num Channels TX:", limesdr.get_num_channels())
        print("TX antennas", limesdr.get_antenna_list())
        limesdr.set_tx(False)
        self.assertFalse(limesdr.get_tx())

        print("Num Channels RX:", limesdr.get_num_channels())
        limesdr.CHANNEL = 0
        print("Enable RX Channel 0:", limesdr.enable_channel(True, False, 0))

        #path = os.path.realpath(os.path.join(__file__, "..", "..", "src", "urh", "dev", "native", "lime.ini"))
        #print(path)
        #limesdr.load_config(path)
        #limesdr.save_config("/tmp/lime_test.ini")

        clocks = ["LMS_CLOCK_REF", "LMS_CLOCK_SXR", "LMS_CLOCK_SXT", "LMS_CLOCK_CGEN", "LMS_CLOCK_RXTSP", "LMS_CLOCK_TXTSP"]

        for i, clock in enumerate(clocks):
            print(clock, limesdr.get_clock_freq(i))

        limesdr.print_last_error()
        print("RX Sample Rate Range:", limesdr.get_sample_rate_range())
        print("RX Channel 0 Sample Rate:", limesdr.get_sample_rate())
        print("Set Sample Rate:", limesdr.set_sample_rate(2e6))
        print("RX Channel 0 Sample Rate:", limesdr.get_sample_rate())

        limesdr.print_last_error()
        print("RX Frequency Range:", limesdr.get_center_frequency_range())
        print("RX 0 center freq:", limesdr.get_center_frequency())
        print("RX 0 set center freq:", limesdr.set_center_frequency(433.92e6))
        print("RX 0 center freq:", limesdr.get_center_frequency())

        limesdr.print_last_error()
        print("RX 0 gain", limesdr.get_normalized_gain())
        print("RX 0 set gain", limesdr.set_normalized_gain(0.5))
        print("RX 0 gain", limesdr.get_normalized_gain())

        limesdr.print_last_error()
        print("RX Bandwidth Range", limesdr.get_lpf_bandwidth_range())
        print("RX 0 Bandwidth", limesdr.get_lpf_bandwidth())
        print("RX 0 set Bandwidth", limesdr.set_lpf_bandwidth(20e6))
        print("RX 0 Bandwidth", limesdr.get_lpf_bandwidth())

        limesdr.print_last_error()
        print("RX 0 calibrate:", limesdr.calibrate(20e6))

        limesdr.print_last_error()
        antenna_list = limesdr.get_antenna_list()
        print("RX 0 antenna list", antenna_list)
        print("RX 0 current antenna", limesdr.get_antenna(), antenna_list[limesdr.get_antenna()])
        print("RX 0 current antenna BW", limesdr.get_antenna_bw(limesdr.get_antenna()))

        print("Chip Temperature", limesdr.get_chip_temperature())

        parent_conn, child_conn = Pipe()

        for _ in range(2):
            limesdr.print_last_error()
            print("Setup stream", limesdr.setup_stream(1000))
            print("Start stream", limesdr.start_stream())
            limesdr.recv_stream(child_conn, 1000, 100)
            print("Stop stream", limesdr.stop_stream())
            print("Destroy stream", limesdr.destroy_stream())

            print(parent_conn.recv_bytes())

        limesdr.set_tx(True)
        self.assertTrue(limesdr.get_tx())
        samples_to_send = np.ones(32768, dtype=np.complex64)
        for _ in range(2):
            limesdr.print_last_error()
            print("Setup stream", limesdr.setup_stream(4000000000))
            print("Start stream", limesdr.start_stream())
            print("Send samples", limesdr.send_stream(samples_to_send.view(np.float32), 100))
            print("Stop stream", limesdr.stop_stream())
            print("Destroy stream", limesdr.destroy_stream())

        print("-" * 20)
        print("Close:", limesdr.close())

if __name__ == "__main__":
    unittest.main()
