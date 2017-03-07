import numpy as np

from urh.dev.native.Device import Device
from urh.util.Logger import logger

import socket
import select

class RTLSDRTCP(Device):
    BYTES_PER_SAMPLE = 2  # RTLSDR device produces 8 bit unsigned IQ data
    MAXDATASIZE = 65536
    ENDIAN = "big"
    RTL_TCP_CONSTS = ["NULL", "centerFreq", "sampleRate", "tunerGainMode", "tunerGain", "freqCorrection", "tunerIFGain",
                      "testMode", "agcMode", "directSampling", "offsetTuning", "rtlXtalFreq", "tunerXtalFreq",
                      "gainByIndex", "bandwidth", "biasTee"]

    def receive_sync(self, data_connection, ctrl_connection, device_number: int, center_freq: int, sample_rate: int,
                     gain: int):
        # connect and initialize rtl_tcp
        self.open(self.device_ip, self.port)
        if self.socket_is_open:
            self.device_number = device_number
            self.set_parameter("centerFreq", int(center_freq))
            self.set_parameter("sampleRate", int(sample_rate))
            self.set_parameter("bandwidth", int(sample_rate)) # set bandwidth equal to sample_rate
            self.set_parameter("tunerGain", int(gain))
            #self.set_parameter("freqCorrection", int(freq_correction_in_ppm)) # TODO: add ppm value as parameter to this function
            exit_requested = False

            while not exit_requested:
                while ctrl_connection.poll():
                    result = self.process_command(ctrl_connection.recv())
                    if result == "stop":
                        exit_requested = True
                        break

                if not exit_requested:
                    data_connection.send_bytes(self.read_sync())

            logger.debug("RTLSDRTCP: closing device")
            self.close()
        else:
            ctrl_connection.send("Could not connect to rtl_tcp:404")
        ctrl_connection.send("close:0")
        data_connection.close()
        ctrl_connection.close()

    def process_command(self, command):
        logger.debug("RTLSDRTCP: {}".format(command))
        if command == "stop":
            return "stop"

        tag, value = command.split(":")
        if tag == "center_freq":
            logger.info("RTLSDRTCP: Set center freq to {0}".format(int(value)))
            return self.set_parameter("centerFreq", int(value))

        elif tag == "tuner_gain":
            logger.info("RTLSDRTCP: Set tuner gain to {0}".format(int(value)))
            return self.set_parameter("tunerGain", int(value))

        elif tag == "sample_rate":
            logger.info("RTLSDRTCP: Set sample_rate to {0}".format(int(value)))
            return self.set_parameter("sampleRate", int(value))

        elif tag == "tuner_bandwidth":
            logger.info("RTLSDRTCP: Set bandwidth to {0}".format(int(value)))
            return self.set_parameter("bandwidth", int(value))

        elif tag == "freq_correction":
            logger.info("RTLSDRTCP: Set ppm correction to {0}".format(int(value)))
            return self.set_parameter("freqCorrection", int(value))

    def __init__(self, freq, gain, srate, device_number, is_ringbuffer=False):
        super().__init__(0, freq, gain, srate, is_ringbuffer)

        # default class parameters
        self.receive_process_function = self.receive_sync
        self.device_number = device_number
        self.socket_is_open = False
        self.success = 0

        # maximum device parameters
        self._max_frequency = 6e9
        self._max_sample_rate = 3200000
        self._max_frequency = 6e9
        self._max_bandwidth = 3200000
        self._max_gain = 500  # Todo: Consider get_tuner_gains for allowed gains here

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.device_number, self.frequency, self.sample_rate, self.gain

    def open(self, hostname="127.0.0.1", port=1234):
        if not self.socket_is_open:
            try:
                # Create socket and connect
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
                #self.sock.settimeout(1.0)  # Timeout 1s
                self.sock.connect((hostname, port))
            except Exception as e:
                self.socket_is_open = False
                logger.info("Could not connect to rtl_tcp at {0}:{1} ({2})".format(hostname, port, e))
                self.errors.add("Could not connect to rtl_tcp at {0}:{1} ({2})".format(hostname, port, e))
                return False

            try:
                # Receive rtl_tcp initial data
                init_data = self.sock.recv(self.MAXDATASIZE)

                if len(init_data) != 12:
                    return False
                if init_data[0:4] != b'RTL0':
                    return False

                # Extract tuner name
                tuner_number = int.from_bytes(init_data[4:8], self.ENDIAN)
                if tuner_number == 1:
                    self.tuner = "E4000"
                elif tuner_number == 2:
                    self.tuner = "FC0012"
                elif tuner_number == 3:
                    self.tuner = "FC0013"
                elif tuner_number == 4:
                    self.tuner = "FC2580"
                elif tuner_number == 5:
                    self.tuner = "R820T"
                elif tuner_number == 6:
                    self.tuner = "R828D"
                else:
                    self.tuner = "Unknown"

                # Extract IF and RF gain
                self.if_gain = int.from_bytes(init_data[8:10], self.ENDIAN)
                self.rf_gain = int.from_bytes(init_data[10:12], self.ENDIAN)

                logger.info("Connected to rtl_tcp at {0}:{1} (Tuner: {2}, RF-Gain: {3}, IF-Gain: {4})".format(hostname, port, self.tuner, self.rf_gain, self.if_gain))
                # Show this in error message box after refactoring:
                #self.errors.add("Connected to rtl_tcp at {0}:{1} (Tuner: {2}, RF-Gain: {3}, IF-Gain: {4})".format(hostname, port, self.tuner, self.rf_gain, self.if_gain))
            except Exception as e:
                self.socket_is_open = False
                logger.info("This is not a valid rtl_tcp server at {0}:{1} ({2})".format(hostname, port, e))
                return False

            self.socket_is_open = True

    def close(self):
        if self.socket_is_open:
            self.socket_is_open = False
        return self.sock.close()

    def set_parameter(self, param: str, value: int):  # returns error (True/False)
        if self.socket_is_open:
            msg = self.RTL_TCP_CONSTS.index(param).to_bytes(1, self.ENDIAN)     # Set param at bits 0-7
            msg += value.to_bytes(4, self.ENDIAN)                               # Set value at bits 8-39
            try:
                self.sock.sendall(msg)                                          # Send data to rtl_tcp
            except OSError as e:
                self.sock.close()
                logger.info("Could not set parameter {0}:{1} ({2})".format(param, value, e))
                self.errors.add("Could not set parameter {0}:{1} ({2})".format(param, value, e))
                return True
        return False

    def read_sync(self):
        s_read, _, _ = select.select([self.sock], [], [], .1)
        if self.sock in s_read:
            return self.sock.recv(self.MAXDATASIZE)
        else:
            return b''

    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        """
        The raw, captured IQ data is 8 bit unsigned data.

        :return:
        """
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
        result.real = (unpacked['r'] / 127.5) - 1.0
        result.imag = (unpacked['i'] / 127.5) - 1.0
        return result
