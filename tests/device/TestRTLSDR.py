import unittest
import sys
import time

import numpy as np

from urh.util import util

util.set_shared_library_path()

from urh.dev.native.RTLSDR import RTLSDR
from urh.dev.native.lib import rtlsdr


class TestRTLSDR(unittest.TestCase):
    def test_cython_wrapper(self):
        print("Device count:", rtlsdr.get_device_count())
        print("Device name:", rtlsdr.get_device_name(0))
        manufact, product, serial = rtlsdr.get_device_usb_strings(0)
        print("Manufacturer:", manufact)
        print("Product:", product)
        print("Serial", serial)
        print("Index by serial", rtlsdr.get_index_by_serial(serial))
        print("Open:", rtlsdr.open(0))
        print("Reset Buffer:", rtlsdr.reset_buffer())  # IMPORTANT
        print("XTAL Freq:", rtlsdr.get_xtal_freq())
        print("USB device strings", rtlsdr.get_usb_strings())
        print("Center Freq:", rtlsdr.get_center_freq())
        print("Set center freq to 433MHz", rtlsdr.set_center_freq(int(433e6)))
        print("Center Freq:", rtlsdr.get_center_freq())
        print("Freq Correction", rtlsdr.get_freq_correction())
        print("Set Freq Correction to 10", rtlsdr.set_freq_correction(10))
        print("Freq Correction", rtlsdr.get_freq_correction())
        print("tuner type", rtlsdr.get_tuner_type())
        print("tuner_gains", rtlsdr.get_tuner_gains())
        print("set_manual_gain_mode", rtlsdr.set_tuner_gain_mode(1))
        print("tuner gain", rtlsdr.get_tuner_gain())
        print("set gain to 338", rtlsdr.set_tuner_gain(338))
        print("tuner gain", rtlsdr.get_tuner_gain())
        print("set tuner if gain", rtlsdr.set_tuner_if_gain(1, 10))
        print("Sample Rate", rtlsdr.get_sample_rate())
        print("Set Sample Rate to 300k", rtlsdr.set_sample_rate(300 * 10**3))
        print("Sample Rate", rtlsdr.get_sample_rate())
        read_samples = rtlsdr.read_sync(1024)
        print(read_samples)
        rtlsdr.close()

    def test_receive(self):
        rtlsdr_class = RTLSDR(433.92e6, 20, 2e6, device_number=0)
        self.assertEqual(rtlsdr_class.current_recv_index, 0)
        rtlsdr_class.start_rx_mode()
        time.sleep(2)
        rtlsdr_class.stop_rx_mode("Finished")
        index = rtlsdr_class.current_recv_index
        print(rtlsdr_class.current_recv_index)
        self.assertGreater(rtlsdr_class.current_recv_index, 0)
        time.sleep(2)
        self.assertEqual(index, rtlsdr_class.current_recv_index)
        rtlsdr_class.start_rx_mode()
        time.sleep(1)
        self.assertGreater(rtlsdr_class.current_recv_index, index)

    def test_bytes_to_iq(self):
        arr = np.array([0, 0, 127.5, 127.5, 255, 255], dtype=np.uint8)
        self.assertEqual(arr[0], 0)
        self.assertEqual(arr[1], 0)
        self.assertEqual(arr[-1], 255)

        received = arr.tostring()
        self.assertEqual(len(received), len(arr))
        self.assertEqual(np.int8(received[0]), 0)
        self.assertEqual(np.int8(received[1]), 0)
        unpacked = RTLSDR.bytes_to_iq(received, len(received) // 2)

        self.assertEqual(unpacked[0], complex(-1, -1))
        self.assertAlmostEqual(unpacked[1], complex(0, 0), places=1)
        self.assertEqual(unpacked[2], complex(1, 1))

        packed = RTLSDR.iq_to_bytes(unpacked)
        self.assertEqual(received, packed)


if __name__ == "__main__":
    unittest.main()
