import unittest

import time

from urh.util import util

util.set_windows_lib_path()

from urh.dev.native.lib import sdrplay

class TestSDRPlay(unittest.TestCase):
    def test_c_wrapper(self):

        def pycallback():
            print("it works")

        print(sdrplay.get_api_version())
        print(sdrplay.get_devices())

        print("Init stream", sdrplay.init_stream(50, 2e6, 433.92e6, 2e6, 500, pycallback))

        time.sleep(3)
