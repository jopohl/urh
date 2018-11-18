from multiprocessing import Pipe

from urh.util import util
import numpy as np
util.set_shared_library_path()

from urh.dev.native.lib import plutosdr


def test_cython_wrapper():
    descs, uris = plutosdr.scan_devices()
    print("Devices", descs)
    print("Open", plutosdr.open(uris[0]))
    print("Set Freq to 433.92e6", plutosdr.set_center_freq(int(433.92e6)))
    print("Set Sample Rate to 2M", plutosdr.set_sample_rate(int(2.5e6)))
    print("Set bandwidth to 4M", plutosdr.set_bandwidth(int(4e6)))
    print("Set gain to 10", plutosdr.set_rf_gain(10))

    print("prepare rx", plutosdr.setup_rx())

    parent_conn, child_conn = Pipe()

    for i in range(10):
        plutosdr.receive_sync(child_conn)
        data = parent_conn.recv_bytes()
        print(np.frombuffer(data, dtype=np.int16))

    print("stop rx", plutosdr.stop_rx())

if __name__ == '__main__':
    test_cython_wrapper()
