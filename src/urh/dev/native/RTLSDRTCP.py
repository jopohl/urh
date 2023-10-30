import select
import socket

import numpy as np

from urh.dev.native.Device import Device
from urh.util.Logger import logger


class RTLSDRTCP(Device):
    MAXDATASIZE = 65536
    ENDIAN = "big"
    RTL_TCP_CONSTS = [
        "NULL",
        "centerFreq",
        "sampleRate",
        "tunerGainMode",
        "tunerGain",
        "freqCorrection",
        "tunerIFGain",
        "testMode",
        "agcMode",
        "directSampling",
        "offsetTuning",
        "rtlXtalFreq",
        "tunerXtalFreq",
        "gainByIndex",
        "bandwidth",
        "biasTee",
    ]

    DATA_TYPE = np.uint8

    @staticmethod
    def receive_sync(
        data_connection,
        ctrl_connection,
        device_number: int,
        center_freq: int,
        sample_rate: int,
        bandwidth: int,
        gain: int,
        freq_correction: int,
        direct_sampling_mode: int,
        device_ip: str,
        port: int,
    ):
        # connect and initialize rtl_tcp
        sdr = RTLSDRTCP(center_freq, gain, sample_rate, bandwidth, device_number)
        sdr.open(ctrl_connection, device_ip, port)
        if sdr.socket_is_open:
            sdr.device_number = device_number
            sdr.set_parameter("centerFreq", int(center_freq), ctrl_connection)
            sdr.set_parameter("sampleRate", int(sample_rate), ctrl_connection)
            sdr.set_parameter("bandwidth", int(bandwidth), ctrl_connection)
            sdr.set_parameter("freqCorrection", int(freq_correction), ctrl_connection)
            sdr.set_parameter(
                "directSampling", int(direct_sampling_mode), ctrl_connection
            )
            # Gain has to be set last, otherwise it does not get considered by RTL-SDR
            sdr.set_parameter("tunerGain", int(gain), ctrl_connection)
            exit_requested = False

            while not exit_requested:
                while ctrl_connection.poll():
                    result = sdr.process_command(
                        ctrl_connection.recv(), ctrl_connection
                    )
                    if result == "stop":
                        exit_requested = True
                        break

                if not exit_requested:
                    data_connection.send_bytes(sdr.read_sync())

            logger.debug("RTLSDRTCP: closing device")
            sdr.close()
        else:
            ctrl_connection.send("Could not connect to rtl_tcp:404")
        ctrl_connection.send("close:0")
        data_connection.close()
        ctrl_connection.close()

    def process_command(self, command, ctrl_connection, is_tx=False):
        logger.debug("RTLSDRTCP: {}".format(command))
        if command == self.Command.STOP.name:
            return self.Command.STOP

        tag, value = command
        if tag == self.Command.SET_FREQUENCY.name:
            logger.info("RTLSDRTCP: Set center freq to {0}".format(int(value)))
            return self.set_parameter("centerFreq", int(value), ctrl_connection)

        elif tag == self.Command.SET_RF_GAIN.name:
            logger.info("RTLSDRTCP: Set tuner gain to {0}".format(int(value)))
            return self.set_parameter("tunerGain", int(value), ctrl_connection)

        elif tag == self.Command.SET_IF_GAIN.name:
            logger.info("RTLSDRTCP: Set if gain to {0}".format(int(value)))
            return self.set_parameter("tunerIFGain", int(value), ctrl_connection)

        elif tag == self.Command.SET_SAMPLE_RATE.name:
            logger.info("RTLSDRTCP: Set sample_rate to {0}".format(int(value)))
            return self.set_parameter("sampleRate", int(value), ctrl_connection)

        elif tag == self.Command.SET_BANDWIDTH.name:
            logger.info("RTLSDRTCP: Set bandwidth to {0}".format(int(value)))
            return self.set_parameter("bandwidth", int(value), ctrl_connection)

        elif tag == self.Command.SET_FREQUENCY_CORRECTION.name:
            logger.info("RTLSDRTCP: Set ppm correction to {0}".format(int(value)))
            return self.set_parameter("freqCorrection", int(value), ctrl_connection)

        elif tag == self.Command.SET_DIRECT_SAMPLING_MODE.name:
            logger.info("RTLSDRTCP: Set direct sampling mode to {0}".format(int(value)))
            return self.set_parameter("directSampling", int(value), ctrl_connection)

    def __init__(
        self,
        freq,
        gain,
        srate,
        bandwidth,
        device_number,
        resume_on_full_receive_buffer=False,
    ):
        super().__init__(
            center_freq=freq,
            sample_rate=srate,
            bandwidth=bandwidth,
            gain=gain,
            if_gain=1,
            baseband_gain=1,
            resume_on_full_receive_buffer=resume_on_full_receive_buffer,
        )

        # default class parameters
        self.receive_process_function = self.receive_sync
        self.device_number = device_number
        self.socket_is_open = False
        self.success = 0

    @property
    def receive_process_arguments(self):
        return (
            self.child_data_conn,
            self.child_ctrl_conn,
            self.device_number,
            self.frequency,
            self.sample_rate,
            self.bandwidth,
            self.gain,
            self.freq_correction,
            self.direct_sampling_mode,
            self.device_ip,
            self.port,
        )

    def open(self, ctrl_connection, hostname="127.0.0.1", port=1234):
        if not self.socket_is_open:
            try:
                # Create socket and connect
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
                )
                # self.sock.settimeout(1.0)  # Timeout 1s
                self.sock.connect((hostname, port))
            except Exception as e:
                self.socket_is_open = False
                logger.info(
                    "Could not connect to rtl_tcp at {0}:{1} ({2})".format(
                        hostname, port, e
                    )
                )
                ctrl_connection.send(
                    "Could not connect to rtl_tcp at {0} [{1}] ({2}):1".format(
                        hostname, port, e
                    )
                )
                return False

            try:
                # Receive rtl_tcp initial data
                init_data = self.sock.recv(self.MAXDATASIZE)

                if len(init_data) != 12:
                    return False
                if init_data[0:4] != b"RTL0":
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

                logger.info(
                    "Connected to rtl_tcp at {0}:{1} (Tuner: {2}, RF-Gain: {3}, IF-Gain: {4})".format(
                        hostname, port, self.tuner, self.rf_gain, self.if_gain
                    )
                )
                ctrl_connection.send(
                    "Connected to rtl_tcp at {0}[{1}] (Tuner={2}, RF-Gain={3}, IF-Gain={4}):0".format(
                        hostname, port, self.tuner, self.rf_gain, self.if_gain
                    )
                )
            except Exception as e:
                self.socket_is_open = False
                logger.info(
                    "This is not a valid rtl_tcp server at {0}:{1} ({2})".format(
                        hostname, port, e
                    )
                )
                return False

            self.socket_is_open = True

    def close(self):
        if self.socket_is_open:
            self.socket_is_open = False
        return self.sock.close()

    def set_parameter(
        self, param: str, value: int, ctrl_connection
    ):  # returns error (True/False)
        if self.socket_is_open:
            msg = self.RTL_TCP_CONSTS.index(param).to_bytes(
                1, self.ENDIAN
            )  # Set param at bits 0-7
            msg += value.to_bytes(4, self.ENDIAN)  # Set value at bits 8-39
            try:
                self.sock.sendall(msg)  # Send data to rtl_tcp
            except OSError as e:
                self.sock.close()
                logger.info(
                    "Could not set parameter {0}:{1} ({2})".format(param, value, e)
                )
                ctrl_connection.send(
                    "Could not set parameter {0} {1} ({2}):1".format(param, value, e)
                )
                return True
        return False

    def read_sync(self):
        s_read, _, _ = select.select([self.sock], [], [], 0.1)
        if self.sock in s_read:
            return self.sock.recv(self.MAXDATASIZE)
        else:
            return b""

    @staticmethod
    def bytes_to_iq(buffer):
        return np.subtract(np.frombuffer(buffer, dtype=np.int8), 127).reshape(
            (-1, 2), order="C"
        )
