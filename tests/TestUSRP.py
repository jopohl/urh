from multiprocessing.connection import Pipe

from urh.dev.native.lib import usrp
import unittest

class TestUSRP(unittest.TestCase):
    def test_cython_wrapper(self):
        ret_code, devices = usrp.find_devices("")
        print(ret_code, devices)
        self.assertEqual(ret_code, 0)

        usrp.set_tx(False)

        return_code = usrp.open("addr=192.168.10.2")
        print("open", return_code)

        usrp.setup_stream()
        print("Made rx_streame handler")

        print(usrp.get_device_representation())

        parent_conn, child_conn = Pipe()
        for _ in range(3):
            usrp.recv_stream(child_conn, 8192)
            print(parent_conn.recv_bytes())

        usrp.destroy_stream()
        print("Freed rx streamer handler")

        return_code = usrp.close()
        print("close", return_code)


        #self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
