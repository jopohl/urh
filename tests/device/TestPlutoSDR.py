from urh.util import util
import numpy as np
util.set_shared_library_path()

from urh.dev.native.lib import plutosdr


def test_cython_wrapper():
    descs, uris = plutosdr.scan_devices()
    print("Devices", descs)
    print("prepare rx", plutosdr.setup_rx(uris[0]))

    for _ in range(10):
        print(np.frombuffer(plutosdr.receive_sync(), dtype=np.int16))

    print("stop rx", plutosdr.stop_rx())

if __name__ == '__main__':
    test_cython_wrapper()
