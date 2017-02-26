import unittest
from multiprocessing import Pipe

from multiprocessing import Process


def f(conn):
    conn.send([42, None, 'hello'])
    conn.close()

class TestPipe(unittest.TestCase):
    def test_multiprocessing_pipe(self):
        parent_conn, child_conn = Pipe()
        p = Process(target=f, args=(child_conn,))
        p.start()
        print(parent_conn.recv())  # prints "[42, None, 'hello']"
        p.join()
