import unittest

from urh.util import util

util.set_shared_library_path()

from urh.dev.native.lib import bladerf

class TestBladeRF(unittest.TestCase):
    def test_cython_wrapper(self):
        serials = bladerf.get_device_list()
        print("Connected serials", serials)

        print("Open first avail", bladerf.open())
        bladerf.close()

        print("Open first serial", bladerf.open(serials[0]))
        bladerf.close()
