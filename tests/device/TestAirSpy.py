import unittest

import time

from multiprocessing import Queue, Pipe

import numpy as np

from urh.dev.native.lib import airspy


class TestAirSpy(unittest.TestCase):
    def test_cython_wrapper(self):
        result = airspy.open()
        print("Open:", airspy.error_name(result), result)

        sample_rates = airspy.get_sample_rates()
        print("Samples rates:", sample_rates)

        result = airspy.set_sample_rate(10**6)
        print("Set sample rate", airspy.error_name(result), result)

        result = airspy.set_center_frequency(int(433.92e6))
        print("Set center frequency", airspy.error_name(result), result)

        result = airspy.set_if_rx_gain(5)
        print("Set lna gain", airspy.error_name(result), result)

        result = airspy.set_rf_gain(8)
        print("Set mixer gain", airspy.error_name(result), result)

        result = airspy.set_baseband_gain(10)
        print("Set vga gain", airspy.error_name(result), result)

        parent_conn, child_conn = Pipe()

        result = airspy.start_rx(child_conn.send_bytes)
        print("Set start rx", airspy.error_name(result), result)

        time.sleep(0.01)
        print(np.fromstring(parent_conn.recv_bytes(8 * 65536), dtype=np.complex64))

        print("Closing")

        parent_conn.close()
        child_conn.close()

        result = airspy.stop_rx()
        print("Set stop rx", airspy.error_name(result), result)

        result = airspy.close()
        print("Close:", airspy.error_name(result), result)


if __name__ == "__main__":
    unittest.main()
