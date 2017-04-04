import unittest
import sys

if sys.platform == "win32":
    import os

    cur_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
    dll_dir = os.path.realpath(os.path.join(cur_dir, "..", "src", "urh", "dev", "native", "lib", "win"))
    os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']

from urh.dev.native.lib import limesdr


class TestLimeSDR(unittest.TestCase):
    def test_cython_wrapper(self):
        print("Devices:", limesdr.get_device_list())
        # print("Open:", limesdr.open("LimeSDR-USB, media=USB 3.0, module=STREAM, addr=1d50:6108, serial=0009060B0049180A"))
        print("Open:", limesdr.open())
        print("Is Open 0:", limesdr.is_open(0))
        print("Is Open 1:", limesdr.is_open(1))
        print("Close:", limesdr.close())
        print("Is Open 0:", limesdr.is_open(0))
        print("Is Open 1:", limesdr.is_open(1))


if __name__ == "__main__":
    unittest.main()
