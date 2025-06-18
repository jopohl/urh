import unittest

import time

from multiprocessing import Queue, Pipe

import numpy as np

from urh.dev.native.lib import hydrasdr


class TestHydraSDR(unittest.TestCase):
    def test_cython_wrapper(self):
        result = hydrasdr.open()
        print("Open:", hydrasdr.error_name(result), result)

        sample_rates = hydrasdr.get_sample_rates()
        print("Samples rates:", sample_rates)

        result = hydrasdr.set_sample_rate(10**6)
        print("Set sample rate", hydrasdr.error_name(result), result)

        result = hydrasdr.set_center_frequency(int(433.92e6))
        print("Set center frequency", hydrasdr.error_name(result), result)

        result = hydrasdr.set_if_rx_gain(5)
        print("Set lna gain", hydrasdr.error_name(result), result)

        result = hydrasdr.set_rf_gain(8)
        print("Set mixer gain", hydrasdr.error_name(result), result)

        result = hydrasdr.set_baseband_gain(10)
        print("Set vga gain", hydrasdr.error_name(result), result)

        parent_conn, child_conn = Pipe()

        result = hydrasdr.start_rx(child_conn.send_bytes)
        print("Set start rx", hydrasdr.error_name(result), result)

        time.sleep(0.01)
        print(np.fromstring(parent_conn.recv_bytes(8 * 65536), dtype=np.complex64))

        print("Closing")

        parent_conn.close()
        child_conn.close()

        result = hydrasdr.stop_rx()
        print("Set stop rx", hydrasdr.error_name(result), result)

        result = hydrasdr.close()
        print("Close:", hydrasdr.error_name(result), result)


if __name__ == "__main__":
    unittest.main()
