import unittest
from multiprocessing import Pipe

from multiprocessing import Process
from threading import Thread

try:
    from urh.dev.native.lib import rtlsdr
except ImportError:
    import urh.dev.native.lib.rtlsdr_fallback as rtlsdr

import time

from urh.util.Logger import logger


def callback_recv(buffer):
    try:
        print(len(buffer))
    except BrokenPipeError:
        pass
    return 0


def receive_async(callback, connection):
    rtlsdr.open(0)
    rtlsdr.reset_buffer()
    rtlsdr.read_async(callback, connection)
    connection.close()

def receive_sync(connection):
    rtlsdr.open(0)
    rtlsdr.reset_buffer()
    exit_requested = False

    while not exit_requested:
        while connection.poll():
            result = process_command(connection.recv())
            if result == "stop":
                exit_requested = True
                break

        if not exit_requested:
            connection.send_bytes(rtlsdr.read_sync())

    connection.close()

def process_command(command):
    if command == "stop":
        return "stop"

    tag, value = command.split(":")
    if tag == "center_freq":
        logger.info("[RTLSDR] setting center freq to {}".format(int(value)))
        rtlsdr.set_center_freq(int(value))
    elif tag == "tuner_gain":
        logger.info("[RTLSDR] setting tuner_gain to {}".format(int(value)))
        rtlsdr.set_tuner_gain(int(value))
    elif tag == "sample_rate":
        logger.info("[RTLSDR] setting sample rate to {}".format(int(value)))
        rtlsdr.set_sample_rate(int(value))

def read_connection(connection):
    while True:
        try:
            received_bytes = connection.recv_bytes()
            print(received_bytes[0:100])
        except EOFError:
            break

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
        p = Process(target=receive_sync, args=(child_conn, ))
        t = Thread(target=read_connection, args=(parent_conn, ))
        t.daemon = True
        p.daemon = True
        t.start()
        p.start()
        time.sleep(2)
        print("Sending set freq command")
        parent_conn.send("center_freq:{}".format(int(433.92e6)))
        time.sleep(1)
        parent_conn.send("tuner_gain:{}".format(int(20)))
        time.sleep(1)
        parent_conn.send("sample_rate:{}".format(int(2e6)))
        print("Sending stop command")
        parent_conn.send("stop")
        p.join()
        time.sleep(2)
