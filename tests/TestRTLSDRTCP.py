import unittest
import sys
import time

import numpy as np

from urh.dev.native.RTLSDRTCP import RTLSDRTCP

class TestRTLSDRTCP(unittest.TestCase):

    def test_device_communication(self):
        sdr = RTLSDRTCP(0, 0, 0, device_number=0)
        error = 0

        if sdr.set_device_frequency(926000000):
            error += 1

        if sdr.set_device_sample_rate(2000000):
            error += 1

        if sdr.set_bandwidth(2000000):
            error += 1

        if sdr.set_device_gain(30):
            error += 1

        if sdr.set_gain_mode(1):
            error += 1

        if sdr.set_if_gain(30):
            error += 1

        if sdr.set_offset_tuning(1):
            error += 1

        if sdr.set_freq_correction(0):
            error += 1

        sdr.close()
        self.assertEqual(error, 0)

