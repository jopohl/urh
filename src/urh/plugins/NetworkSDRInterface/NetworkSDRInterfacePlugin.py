import socket
import socketserver
import threading
import time

import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from urh import settings
from urh.plugins.Plugin import SDRPlugin
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Message import Message
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh.util.RingBuffer import RingBuffer


class NetworkSDRInterfacePlugin(SDRPlugin):
    DATA_TYPE = np.float32

    NETWORK_SDR_NAME = "Network SDR"  # Display text for device combo box
    show_proto_sniff_dialog_clicked = pyqtSignal()
    sending_status_changed = pyqtSignal(bool)
    sending_stop_requested = pyqtSignal()
    current_send_message_changed = pyqtSignal(int)

    send_connection_established = pyqtSignal()
    receive_server_started = pyqtSignal()
    error_occurred = pyqtSignal(str)

    class MyTCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            size = 2 * np.dtype(NetworkSDRInterfacePlugin.DATA_TYPE).itemsize
            received = self.request.recv(65536 * size)
            self.data = received

            while received:
                received = self.request.recv(65536 * size)
                self.data += received

            if len(self.data) == 0:
                return

            if hasattr(self.server, "received_bits"):
                for data in filter(None, self.data.split(b"\n")):
                    self.server.received_bits.append(
                        NetworkSDRInterfacePlugin.bytearray_to_bit_str(data)
                    )
            else:
                while len(self.data) % size != 0:
                    self.data += self.request.recv(len(self.data) % size)

                received = np.frombuffer(
                    self.data, dtype=NetworkSDRInterfacePlugin.DATA_TYPE
                )
                received = received.reshape((len(received) // 2, 2))

                if len(received) + self.server.current_receive_index >= len(
                    self.server.receive_buffer
                ):
                    self.server.current_receive_index = 0

                self.server.receive_buffer[
                    self.server.current_receive_index : self.server.current_receive_index
                    + len(received)
                ] = received
                self.server.current_receive_index += len(received)

    def __init__(
        self,
        raw_mode=False,
        resume_on_full_receive_buffer=False,
        spectrum=False,
        sending=False,
    ):
        """

        :param raw_mode: If true, sending and receiving raw samples if false bits are received/sent
        """
        super().__init__(name="NetworkSDRInterface")
        self.client_ip = self.qsettings.value(
            "client_ip", defaultValue="127.0.0.1", type=str
        )
        self.server_ip = ""

        self.samples_to_send = None  # set in virtual device constructor

        self.client_port = self.qsettings.value(
            "client_port", defaultValue=2222, type=int
        )
        self.server_port = self.qsettings.value(
            "server_port", defaultValue=4444, type=int
        )

        self.is_in_spectrum_mode = spectrum
        self.resume_on_full_receive_buffer = resume_on_full_receive_buffer
        self.__is_sending = False
        self.__sending_interrupt_requested = False

        self.sending_repeats = 1  # only used in raw mode
        self.current_sent_sample = 0
        self.current_sending_repeat = 0

        self.sending_is_continuous = False
        self.continuous_send_ring_buffer = None
        self.num_samples_to_send = None  # Only used for continuous send mode

        self.raw_mode = raw_mode
        if not sending:
            if self.raw_mode:
                num_samples = settings.get_receive_buffer_size(
                    self.resume_on_full_receive_buffer, self.is_in_spectrum_mode
                )
                try:
                    self.receive_buffer = IQArray(
                        None, dtype=self.DATA_TYPE, n=num_samples
                    )
                except MemoryError:
                    logger.warning(
                        "Could not allocate buffer with {0:d} samples, trying less..."
                    )
                    i = 0
                    while True:
                        try:
                            i += 2
                            self.receive_buffer = IQArray(
                                None, dtype=self.DATA_TYPE, n=num_samples // i
                            )
                            logger.debug(
                                "Using buffer with {0:d} samples instead.".format(
                                    num_samples // i
                                )
                            )
                            break
                        except MemoryError:
                            continue
            else:
                self.received_bits = []

    @property
    def is_sending(self) -> bool:
        return self.__is_sending

    @is_sending.setter
    def is_sending(self, value: bool):
        if value != self.__is_sending:
            self.__is_sending = value
            self.sending_status_changed.emit(self.__is_sending)

    @property
    def sending_finished(self) -> bool:
        return (
            self.current_sending_repeat >= self.sending_repeats
            if self.sending_repeats > 0
            else False
        )

    @property
    def received_data(self):
        if self.raw_mode:
            return self.receive_buffer[: self.current_receive_index]
        else:
            return self.received_bits

    @property
    def current_receive_index(self):
        if hasattr(self, "server") and hasattr(self.server, "current_receive_index"):
            return self.server.current_receive_index
        else:
            return 0

    @current_receive_index.setter
    def current_receive_index(self, value):
        if hasattr(self, "server") and hasattr(self.server, "current_receive_index"):
            self.server.current_receive_index = value
        else:
            pass

    def free_data(self):
        if self.raw_mode:
            self.receive_buffer = IQArray(None, dtype=self.DATA_TYPE, n=0)
        else:
            self.received_bits[:] = []

    def create_connects(self):
        self.settings_frame.lineEditClientIP.setText(self.client_ip)
        self.settings_frame.spinBoxClientPort.setValue(self.client_port)
        self.settings_frame.spinBoxServerPort.setValue(self.server_port)

        self.settings_frame.lineEditClientIP.editingFinished.connect(
            self.on_linedit_client_ip_editing_finished
        )
        self.settings_frame.lineEditServerIP.editingFinished.connect(
            self.on_linedit_server_ip_editing_finished
        )
        self.settings_frame.spinBoxClientPort.editingFinished.connect(
            self.on_spinbox_client_port_editing_finished
        )
        self.settings_frame.spinBoxServerPort.editingFinished.connect(
            self.on_spinbox_server_port_editing_finished
        )

        self.settings_frame.lOpenProtoSniffer.linkActivated.connect(
            self.on_lopenprotosniffer_link_activated
        )

    def start_tcp_server_for_receiving(self):
        self.server = socketserver.TCPServer(
            (self.server_ip, self.server_port), self.MyTCPHandler
        )
        self.server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self.raw_mode:
            self.server.receive_buffer = self.receive_buffer
            self.server.current_receive_index = 0
        else:
            self.server.received_bits = self.received_bits

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        logger.debug("Started TCP server for receiving")

        self.receive_server_started.emit()

    def stop_tcp_server(self):
        if hasattr(self, "server"):
            logger.debug("Shutdown TCP server")
            self.server.shutdown()
            self.server.server_close()
        if hasattr(self, "server_thread"):
            self.server_thread.join()

    def send_data(self, data, sock: socket.socket) -> str:
        try:
            sock.sendall(data)
            return ""
        except Exception as e:
            return str(e)

    def send_raw_data(self, data: IQArray, num_repeats: int):
        byte_data = data.to_bytes()
        rng = (
            iter(int, 1) if num_repeats <= 0 else range(0, num_repeats)
        )  # <= 0 = forever

        sock = self.prepare_send_connection()
        if sock is None:
            return

        try:
            for _ in rng:
                if self.__sending_interrupt_requested:
                    break
                self.send_data(byte_data, sock)
                self.current_sent_sample = len(data)
                self.current_sending_repeat += 1
        finally:
            self.shutdown_socket(sock)

    def prepare_send_connection(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((self.client_ip, self.client_port))
            return sock
        except Exception as e:
            msg = "Could not establish connection " + str(e)
            self.error_occurred.emit(msg)
            logger.error(msg)
            return None

    @staticmethod
    def shutdown_socket(sock):
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()

    def send_raw_data_continuously(
        self, ring_buffer: RingBuffer, num_samples_to_send: int, num_repeats: int
    ):
        rng = (
            iter(int, 1) if num_repeats <= 0 else range(0, num_repeats)
        )  # <= 0 = forever
        samples_per_iteration = 65536 // 2
        sock = self.prepare_send_connection()
        if sock is None:
            return

        try:
            for _ in rng:
                if self.__sending_interrupt_requested:
                    break

                while (
                    num_samples_to_send is None
                    or self.current_sent_sample < num_samples_to_send
                ):
                    while (
                        ring_buffer.is_empty and not self.__sending_interrupt_requested
                    ):
                        time.sleep(0.1)

                    if self.__sending_interrupt_requested:
                        break

                    if num_samples_to_send is None:
                        n = samples_per_iteration
                    else:
                        n = max(
                            0,
                            min(
                                samples_per_iteration,
                                num_samples_to_send - self.current_sent_sample,
                            ),
                        )

                    data = ring_buffer.pop(n, ensure_even_length=True)
                    if len(data) > 0:
                        self.send_data(data, sock)
                        self.current_sent_sample += len(data)

                self.current_sending_repeat += 1
                self.current_sent_sample = 0

            self.current_sent_sample = num_samples_to_send
        finally:
            self.shutdown_socket(sock)

    def __send_messages(self, messages, sample_rates):
        """

        :type messages: list of Message
        :type sample_rates: list of int
        :param sample_rates: Sample Rate for each messages, this is needed to calculate the wait time,
                             as the pause for a message is given in samples
        :return:
        """
        self.is_sending = True
        sock = self.prepare_send_connection()
        if sock is None:
            return
        try:
            for i, msg in enumerate(messages):
                if self.__sending_interrupt_requested:
                    break
                assert isinstance(msg, Message)
                wait_time = msg.pause / sample_rates[i]

                self.current_send_message_changed.emit(i)
                error = self.send_data(
                    self.bit_str_to_bytearray(msg.encoded_bits_str) + b"\n", sock
                )
                if not error:
                    logger.debug("Sent message {0}/{1}".format(i + 1, len(messages)))
                    logger.debug("Waiting message pause: {0:.2f}s".format(wait_time))
                    if self.__sending_interrupt_requested:
                        break
                    time.sleep(wait_time)
                else:
                    logger.critical(
                        "Could not connect to {0}:{1}".format(
                            self.client_ip, self.client_port
                        )
                    )
                    break
            logger.debug("Sending finished")
        finally:
            self.is_sending = False
            self.shutdown_socket(sock)

    def start_message_sending_thread(self, messages, sample_rates):
        """

        :type messages: list of Message
        :type sample_rates: list of int
        :param sample_rates: Sample Rate for each messages, this is needed to calculate the wait time,
                             as the pause for a message is given in samples
        :return:
        """
        self.__sending_interrupt_requested = False
        self.sending_thread = threading.Thread(
            target=self.__send_messages, args=(messages, sample_rates)
        )
        self.sending_thread.daemon = True
        self.sending_thread.start()

        self.send_connection_established.emit()

    def start_raw_sending_thread(self):
        self.__sending_interrupt_requested = False
        if self.sending_is_continuous:
            self.sending_thread = threading.Thread(
                target=self.send_raw_data_continuously,
                args=(
                    self.continuous_send_ring_buffer,
                    self.num_samples_to_send,
                    self.sending_repeats,
                ),
            )
        else:
            self.sending_thread = threading.Thread(
                target=self.send_raw_data,
                args=(self.samples_to_send, self.sending_repeats),
            )

        self.sending_thread.daemon = True
        self.sending_thread.start()

        self.send_connection_established.emit()

    def stop_sending_thread(self):
        self.__sending_interrupt_requested = True

        if hasattr(self, "sending_thread"):
            self.sending_thread.join()

        self.sending_stop_requested.emit()

    @staticmethod
    def bytearray_to_bit_str(arr: bytearray) -> str:
        return "".join("{:08b}".format(a) for a in arr)

    @staticmethod
    def bit_str_to_bytearray(bits: str) -> bytearray:
        bits += "0" * ((8 - len(bits) % 8) % 8)
        return bytearray((int(bits[i : i + 8], 2) for i in range(0, len(bits), 8)))

    def on_linedit_client_ip_editing_finished(self):
        ip = self.settings_frame.lineEditClientIP.text()
        self.client_ip = ip
        self.qsettings.setValue("client_ip", self.client_ip)

    def on_linedit_server_ip_editing_finished(self):
        # Does nothing, because field is disabled
        ip = self.settings_frame.lineEditServerIP.text()
        self.server_ip = ip
        self.qsettings.setValue("server_ip", self.server_ip)

    def on_spinbox_client_port_editing_finished(self):
        self.client_port = self.settings_frame.spinBoxClientPort.value()
        self.qsettings.setValue("client_port", str(self.client_port))

    def on_spinbox_server_port_editing_finished(self):
        self.server_port = self.settings_frame.spinBoxServerPort.value()
        self.qsettings.setValue("server_port", str(self.server_port))

    @pyqtSlot(str)
    def on_lopenprotosniffer_link_activated(self, link: str):
        if link == "open_proto_sniffer":
            self.show_proto_sniff_dialog_clicked.emit()
