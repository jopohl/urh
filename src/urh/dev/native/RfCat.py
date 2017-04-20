import numpy as np

from urh.dev.native.Device import Device
from urh.util.Logger import logger

from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty
import time

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


class RFCAT(Device):
    DATA_RATE_DIVISOR = 1000
    BYTES_PER_SAMPLE = 1

    @staticmethod
    def receive_sync(data_connection, ctrl_connection, device_number: int, center_freq: int, sample_rate: int,
                     gain: int, modulation: str, syncmode: int):
        # connect and initialize rtl_tcp
        sdr = RFCAT(center_freq, gain, sample_rate, device_number)
        sdr.open(ctrl_connection, data_connection)
        if sdr.thread_is_open:
            sdr.device_number = device_number
            # Set standard parameter
            sdr.set_parameter("d.setMdmModulation({})".format(modulation), ctrl_connection)
            sdr.set_parameter("d.setFreq({})".format(int(center_freq)), ctrl_connection)
            sdr.set_parameter("d.setMdmSyncMode({})".format(syncmode), ctrl_connection)
            sdr.set_parameter("d.setMdmDRate({})".format(int(sample_rate//RFCAT.DATA_RATE_DIVISOR)), ctrl_connection)
            sdr.set_parameter("d.setMaxPower()", ctrl_connection) # we want power

            exit_requested = False

            while not exit_requested:
                while ctrl_connection.poll():
                    result = sdr.process_command(ctrl_connection.recv(), ctrl_connection)
                    if result == "stop":
                        exit_requested = True
                        break

                if not exit_requested:
                    # data_connection.send_bytes(sdr.read_sync())
                    sdr.read_async()

            logger.debug("RFCAT: closing device")
            sdr.close()
        else:
            ctrl_connection.send("Could not connect to RFCAT:404")
        ctrl_connection.send("close:0")
        data_connection.close()
        ctrl_connection.close()

    def process_command(self, command, ctrl_connection, is_tx=True):
        logger.debug("RFCAT: {}".format(command))
        if command == self.Command.STOP.name:
            return self.Command.STOP

        tag, value = command
        if tag == self.Command.SET_FREQUENCY.name:
            logger.info(">>> d.setFreq({})".format(int(value)))
            return self.set_parameter("d.setFreq({})".format(int(value)), ctrl_connection)

        elif tag == self.Command.SET_RF_GAIN.name or tag == self.Command.SET_IF_GAIN.name:
            logger.info(">>> d.setMaxPower()")
            #return self.set_parameter("print(d.reprRadioConfig())", ctrl_connection)  #TODO: Remove, just for testing
            return self.set_parameter("d.setMaxPower()", ctrl_connection)  #Set max power!

        elif tag == self.Command.SET_MODULATION.name:
            logger.info(">>> d.setMdmModulation({})".format(value))
            return self.set_parameter("d.setMdmModulation({})".format(value), ctrl_connection)

        elif tag == self.Command.SET_SAMPLE_RATE.name:
            logger.info(">>> d.setMdmDRate({})".format(int(value)))
            return self.set_parameter("d.setMdmDRate({})".format(int(value//RFCAT.DATA_RATE_DIVISOR)), ctrl_connection)

        elif tag == self.Command.SET_SYNCMODE.name:
            logger.info(">>> d.setMdmSyncMode({})".format(value))
            return self.set_parameter("d.setMdmSyncMode({})".format(value), ctrl_connection)


    def __init__(self, freq, gain, srate, device_number, is_ringbuffer=False):
        super().__init__(center_freq=freq, sample_rate=srate, bandwidth=0,
                         gain=gain, if_gain=1, baseband_gain=1, is_ringbuffer=is_ringbuffer)

        # default class parameters
        self.receive_process_function = self.receive_sync
        self.device_number = device_number
        self.thread_is_open = False
        self.initialized = False
        self.ready = True
        self.success = 0

        self.modulation = "MOD_ASK_OOK"
        self.syncmode = 0

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.device_number, self.frequency, self.sample_rate, \
               self.gain, self.modulation, self.syncmode

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
                    print("DEBUG:", line)
                    data_start = str(line).find("'")
                    if data_start == -1:
                        logger.info(line)
                    else:
                        # Got data!
                        data = line[data_start+1:-2]
                        logger.info(data)
                        self.data_connection.send_bytes(data)

    def open(self, ctrl_connection, data_connection):
        if not self.thread_is_open:
            self.p = Popen(['rfcat', '-r'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self.rq = Queue()
            self.wq = Queue()

            self.t_stdout = Thread(target=RFCAT.readq, args=(self.p.stdout, self.rq))
            self.t_stdout.daemon = True
            self.t_stdout.start()

            ## Using this shows all the rfcat errors and exceptions -> unusable
            self.t_stderr = Thread(target=RFCAT.readq, args=(self.p.stderr, self.rq))
            self.t_stderr.daemon = True
            self.t_stderr.start()

            self.t_stdin = Thread(target=RFCAT.writeq, args=(self.p.stdin, self.wq))
            self.t_stdin.daemon = True
            self.t_stdin.start()

            self.t_main = Thread(target=self.main_thread) #, args=(data_connection))
            self.t_main.daemon = True
            self.t_main.start()

            self.ctrl_connection = ctrl_connection
            self.data_connection = data_connection
            self.thread_is_open = True

    def close(self):
        if self.socket_is_open:
            try:
                self.t_main.stop()
                self.t_stdout.stop()
                self.t_stderr.stop()
                self.t_stdin.stop()
                self.socket_is_open = False
            except:
                logger.info("Could not close threads:1")

    def set_parameter(self, param: str, ctrl_connection, log=True):  # returns error (True/False)
        # Wait until ready
        if not self.thread_is_open or not self.initialized or not self.ready:
            while not self.thread_is_open or not self.initialized:
                time.sleep(0.1)

        # Send data to queue
        try:
            self.wq.put(param)
            self.ready = False
            if log:
                ctrl_connection.send(param)
                logger.info(param)
        except OSError as e:
            logger.info("Could not set parameter {0}:{1} ({2})".format(param, e))
            ctrl_connection.send("Could not set parameter {0} {1} ({2}):1".format(param, e))
            return True
        return False

    def read_async(self):
        self.set_parameter("d.RFrecv({})[0]".format(500), self.ctrl_connection, log=False)

    # @staticmethod
    # def unpack_complex(buffer, nvalues: int):
    #     """
    #     The raw, captured IQ data is 8 bit unsigned data.
    #
    #     :return:
    #     """
    #     result = np.empty(nvalues, dtype=np.complex64)
    #     unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
    #     result.real = (unpacked['r'] / 127.5) - 1.0
    #     result.imag = (unpacked['i'] / 127.5) - 1.0
    #     return result
