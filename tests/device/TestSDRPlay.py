import unittest

from urh.util import util

util.set_windows_lib_path()

from urh.dev.native.lib import sdrplay

class TestSDRPlay(unittest.TestCase):
    def test_c_wrapper(self):
        print(sdrplay.get_api_version())
        print(sdrplay.get_devices())