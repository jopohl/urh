from Queue import Queue, Empty
from threading import Thread
import sys
import time


class InputHandlerThread(Thread):
    def __init__(self, device):
        Thread.__init__(self)
        self.queue = Queue()
        self.device = device
        self.daemon = True

        t = Thread(target=self.enqueue_input, args=(sys.stdin, self.queue,))
        t.daemon = True  # thread dies with the program
        t.start()

    def enqueue_input(self, inp, queue):
        for line in iter(inp.readline, b''):
            queue.put(line)
        inp.close()

    def read_input(self):
        result = []
        while True:
            try:
                result.append(self.queue.get_nowait())
            except Empty:
                break

        result = b"".join(result)
        return result.decode("utf-8")

    def run(self):
        while True:
            input_commands = self.read_input().split("\n")

            for i in input_commands:
                if len(i) > 0:
                    if i.startswith("SR:"):
                        try:
                            v = float(i.replace("SR:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_samp_rate(v)
                    elif i.startswith("G:"):
                        try:
                            v = int(i.replace("G:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_gain(v)
                    elif i.startswith("IFG:"):
                        try:
                            v = int(i.replace("IFG:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_if_gain(v)
                    elif i.startswith("BBG:"):
                        try:
                            v = int(i.replace("BBG:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_baseband_gain(v)
                    elif i.startswith("BW:"):
                        try:
                            v = float(i.replace("BW:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_bw(v)
                    elif i.startswith("F:"):
                        try:
                            v = float(i.replace("F:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_freq(v)
                    elif i.startswith("FC:"):
                        try:
                            v = float(i.replace("FC:", "").split(" ")[-1])
                        except ValueError:
                            v = 1
                        self.device.set_freq_correction(v)
                    elif i.startswith("DSM:"):
                        print("Gnuradio does not support setting direct sampling mode live.")

            time.sleep(0.1)

