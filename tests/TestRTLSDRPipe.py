import unittest
from multiprocessing import Pipe
import sys

from multiprocessing import Process


import time

if sys.platform == "win32":
    import os
    cur_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
    dll_dir = os.path.realpath(os.path.join(cur_dir, "..", "src", "urh", "dev", "native", "lib", "win"))
    os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']


from urh.dev.native.lib import rtlsdr

def callback_recv(buffer):
    try:
        print(buffer)
    except BrokenPipeError:
        pass
    return 0


def receive_async(callback, connection):
    rtlsdr.open(0)
    rtlsdr.reset_buffer()
    rtlsdr.read_async(callback, connection)
    connection.close()


def f(child_conn):
    ctrl_command = b""
    while ctrl_command != b"stop":
        child_conn.send_bytes(bytearray([1, 2, 3, 4, 5]))
        time.sleep(0.1)
        if child_conn.poll():
            ctrl_command = child_conn.recv_bytes()
            print("Got from server", ctrl_command)

    print("Stopping....")
    child_conn.send("goodbye")
    child_conn.close()


class TestPipe(unittest.TestCase):
    def test_multiprocessing_pipe(self):
        parent_conn, child_conn = Pipe()
        p = Process(target=f, args=(child_conn,))
        p.start()
        for _ in range(5):
            while parent_conn.poll():
                print("Got from client", parent_conn.recv_bytes())  # prints "[42, None, 'hello']"
            time.sleep(1)
        parent_conn.send_bytes(b"stop")
        p.join()


    def test_rtl_sdr_with_pipe(self):
        parent_conn, child_conn = Pipe()
        p = Process(target=receive_async, args=(callback_recv, child_conn))
        p.start()
        time.sleep(2)
        print("Sending stop command")
        parent_conn.send_bytes(b"stop")
        p.join()
        time.sleep(2)
