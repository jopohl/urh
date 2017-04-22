from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

## rfcat commands
# freq = 433920000
# mod = "MOD_ASK_OOK"
# pktlen = 10
# syncmode = 0
# syncbytes = "\xCA\xFE\xAF\xFE"
# baud = 4800
# sendbytes = "\xCA\xFE\xAF\xFE"
# num_preamble = 0
#
# cmd_ping = "d.ping()"
# cmd_freq = "d.setFreq({})".format(freq)
# cmd_mod = "d.setMdmModulation({})".format(mod)
# cmd_pktlen = "d.makePktFLEN({})".format(pktlen)
# cmd_syncmode = "d.setMdmSyncMode({})".format(syncmode)
# cmd_syncbytes = "d.setMdmSyncWord({})".format(syncbytes)
# cmd_baud = "d.setMdmDRate({})".format(baud)
# cmd_sendbytes = "d.RFxmit('{}')".format(sendbytes)
# cmd_maxpower = "d.setMaxPower()"
# cmd_recvbytes = "d.RFrecv()[0]"
# cmd_preamble = "d.setMdmNumPreamble({})".format(num_preamble)
# cmd_showconfig = "print d.reprRadioConfig()"

import time
import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
import socket

from urh import constants
from urh.plugins.Plugin import SDRPlugin
from urh.signalprocessing.Message import Message
from urh.util.Errors import Errors
from urh.util.Logger import logger


class RfCatPlugin(SDRPlugin):
    rcv_index_changed = pyqtSignal(int, int) # int arguments are just for compatibility with native and grc backend
    show_proto_sniff_dialog_clicked = pyqtSignal()
    sending_status_changed = pyqtSignal(bool)
    sending_stop_requested = pyqtSignal()
    current_send_message_changed = pyqtSignal(int)

    def __init__(self, raw_mode=False, spectrum=False):
        super().__init__(name="RfCat")

        self.thread_is_open = False
        self.initialized = False
        self.ready = True
        self.__is_sending = False
        self.__sending_interrupt_requested = False
        self.current_sent_sample = 0
        self.current_sending_repeat = 0

    @property
    def is_sending(self) -> bool:
        return self.__is_sending

    @is_sending.setter
    def is_sending(self, value: bool):
        if value != self.__is_sending:
            self.__is_sending = value
            self.sending_status_changed.emit(self.__is_sending)

    def free_data(self):
        if self.raw_mode:
            self.receive_buffer = np.empty(0)
        else:
            self.received_bits[:] = []

    @staticmethod
    def readq(fd, queue):
        while 1:
            queue.put(fd.readline())

    @staticmethod
    def writeq(fd, queue):
        while 1:
            try:
                buf = queue.get(timeout=.01)
                if buf != "":
                    fd.write(buf.encode("utf8") + b"\n")
                    fd.flush()
            except Empty:
                pass

    def main_thread(self):
        self.initialized = False
        while 1:
            try:
                line = self.rq.get(timeout=.01)  # .get_nowait()
            except Empty:
                pass
            else:
                if self.initialized == False and not b"Error" in line:
                    self.initialized = True

                if self.initialized:
                    self.ready = True
                    data_start = str(line).find("'")
                    if data_start == -1:
                        logger.info(line)
                    else:
                        # Got data!
                        data = line[data_start + 1:-2]
                        logger.info(data)
                        #self.data_connection.send_bytes(data)

    def open_rfcat(self): #, ctrl_connection, data_connection):
        if not self.thread_is_open:
            self.p = Popen(['rfcat', '-r'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self.rq = Queue()
            self.wq = Queue()

            self.t_stdout = Thread(target=RfCatPlugin.readq, args=(self.p.stdout, self.rq))
            self.t_stdout.daemon = True
            self.t_stdout.start()

            ## Using this shows all the rfcat errors and exceptions -> unusable
            # self.t_stderr = Thread(target=RfCatPlugin.readq, args=(self.p.stderr, self.rq))
            # self.t_stderr.daemon = True
            # self.t_stderr.start()

            self.t_stdin = Thread(target=RfCatPlugin.writeq, args=(self.p.stdin, self.wq))
            self.t_stdin.daemon = True
            self.t_stdin.start()

            self.t_main = Thread(target=self.main_thread)  # , args=(data_connection))
            self.t_main.daemon = True
            self.t_main.start()

            self.thread_is_open = True

    def close_rfcat(self):
        if self.thread_is_open:
            try:
                self.t_main.stop()
                self.t_stdout.stop()
                # self.t_stderr.stop()
                self.t_stdin.stop()
                self.socket_is_open = False
            except:
                logger.info("Could not close threads:1")

    def set_parameter(self, param: str, log=True):  # returns error (True/False)
        # Wait until ready
        if not self.thread_is_open or not self.initialized or not self.ready:
            while not self.thread_is_open or not self.initialized:
                time.sleep(0.1)

        # Send data to queue
        try:
            self.wq.put(param)
            self.ready = False
            if log:
                  logger.info(param)
        except OSError as e:
            logger.info("Could not set parameter {0}:{1} ({2})".format(param, e))
            return True
        return False

    def read_async(self):
        self.set_parameter("d.RFrecv({})[0]".format(500), log=False)

    def send_data(self, data) -> str:
        ### Setup RfCat device

        # Get current modulation and translate to
        ## ASK -> "MOD_ASK_OOK"
        ## FSK -> "MOD_GFSK"    # better MOD_2FSK?
        ## PSK -> "MOD_MSK"
        modulation = "MOD_ASK_OOK"
        self.set_parameter("d.setMdmModulation({})".format(modulation))

        # Get current frequency
        center_freq = 433920000
        self.set_parameter("d.setFreq({})".format(int(center_freq)))

        # Disable syncword and preamble
        self.set_parameter("d.setMdmSyncMode(0)")

        # Get values for sample_rate and bitlength, then calculate datarate

        sample_rate = 2000000
        bitlength = 500
        self.set_parameter("d.setMdmDRate({})".format(int(sample_rate // bitlength)))

        # Set maximum power
        self.set_parameter("d.setMaxPower()")

        # Send data
        #data = '\x8e\x8e\xee\xee\xee\x8e\xee\xee' + '\xee\x88\x88\x88\x80'
        for line in data:
            formatted_line = line
            self.set_parameter("d.RFxmit({})".format(formatted_line))

    def send_raw_data(self, data: np.ndarray, num_repeats: int):
        byte_data = data.tostring()

        if num_repeats == -1:
            # forever
            rng = iter(int, 1)
        else:
            rng = range(0, num_repeats)

        for _ in rng:
            self.send_data(byte_data)
            self.current_sent_sample = len(data)
            self.current_sending_repeat += 1


    def __send_messages(self, messages, sample_rates):
        """

        :type messages: list of Message
        :type sample_rates: list of int
        :param sample_rates: Sample Rate for each messages, this is needed to calculate the wait time,
                             as the pause for a message is given in samples
        :return:
        """
        self.is_sending = True
        for i, msg in enumerate(messages):
            if self.__sending_interrupt_requested:
                break
            assert isinstance(msg, Message)
            wait_time = msg.pause / sample_rates[i]

            self.current_send_message_changed.emit(i)
            error = self.send_data(self.bit_str_to_bytearray(msg.encoded_bits_str))
            if not error:
                logger.debug("Sent message {0}/{1}".format(i+1, len(messages)))
                logger.debug("Waiting message pause: {0:.2f}s".format(wait_time))
                if self.__sending_interrupt_requested:
                    break
                time.sleep(wait_time)
            else:
                self.is_sending = False
                Errors.generic_error("Could not connect to {0}:{1}".format(self.client_ip, self.client_port), msg=error)
                break
        logger.debug("Sending finished")
        self.is_sending = False

    def start_message_sending_thread(self, messages, sample_rates):
        """

        :type messages: list of Message
        :type sample_rates: list of int
        :param sample_rates: Sample Rate for each messages, this is needed to calculate the wait time,
                             as the pause for a message is given in samples
        :return:
        """
        self.__sending_interrupt_requested = False
        self.sending_thread = Thread(target=self.__send_messages, args=(messages, sample_rates))
        self.sending_thread.daemon = True
        self.sending_thread.start()

    def stop_sending_thread(self):
        self.__sending_interrupt_requested = True
        self.sending_stop_requested.emit()

    @staticmethod
    def bytearray_to_bit_str(arr: bytearray) -> str:
        return "".join("{:08b}".format(a) for a in arr)

    @staticmethod
    def bit_str_to_bytearray(bits: str) -> bytearray:
        bits += "0" * ((8 - len(bits) % 8) % 8)
        return bytearray((int(bits[i:i+8], 2) for i in range(0, len(bits), 8)))
