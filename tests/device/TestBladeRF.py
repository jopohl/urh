import unittest

from urh.util import util

util.set_shared_library_path()

from urh.dev.native.lib import bladerf

class TestBladeRF(unittest.TestCase):
    def test_cython_wrapper(self):
        serials = bladerf.get_device_list()
        print("Connected serials", serials)

        bladerf.open()
        print("Num rx channels", bladerf.get_channel_count(False))
        print("num tx channels", bladerf.get_channel_count(True))

        bladerf.set_tx(True)
        bladerf.set_channel(0)
        print("set gain", bladerf.set_gain(20))
        print("get gain", bladerf.get_gain())
        print("set gain", bladerf.set_gain(21))
        print("get gain", bladerf.get_gain())

        bladerf.set_tx(False)
        bladerf.set_channel(1)
        print("Sample Rate", bladerf.get_sample_rate())
        print("Set sample rate to 2e6", bladerf.set_sample_rate(int(2e6)))
        print("sample rate", bladerf.get_sample_rate())
        print("Set sample rate to 40e6", bladerf.set_sample_rate(int(40e6)))
        print("sample rate", bladerf.get_sample_rate())
        print("Set sample rate to 200e6", bladerf.set_sample_rate(int(200e6)))
        print("sample rate", bladerf.get_sample_rate())


        bladerf.close()
