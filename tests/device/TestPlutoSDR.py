from urh.util import util

util.set_shared_library_path()

from urh.dev.native.lib import plutosdr


def test_cython_wrapper():
    descs, uris = plutosdr.scan_devices()
    print("Devices", descs)
    print("Get device", plutosdr.get_device(uris[0]))


if __name__ == '__main__':
    test_cython_wrapper()
