from urh.dev.native.lib import usrp
import unittest

class TestUSRP(unittest.TestCase):
    def test_cython_wrapper(self):
        ret_code, devices = usrp.find_devices("")

        print(ret_code, devices)

        self.assertEqual(ret_code, 0)
