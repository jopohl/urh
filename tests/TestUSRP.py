from urh.dev.native.lib import usrp
import unittest

class TestUSRP(unittest.TestCase):
    def test_cython_wrapper(self):
        ret_code, devices = usrp.find_devices("")
        print(ret_code, devices)
        self.assertEqual(ret_code, 0)

        return_code = usrp.open("addr=192.168.10.2")
        print("open", return_code)




        return_code = usrp.close()
        print("close", return_code)

        #usrp.receive("addr=192.168.10.2")
        #self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
