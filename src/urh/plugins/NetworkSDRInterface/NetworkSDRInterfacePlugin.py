import socketserver
import threading

import time

import numpy as np
import psutil
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
import socket

from urh import constants
from urh.plugins.Plugin import SDRPlugin
from urh.signalprocessing.Message import Message
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh.util.SettingsProxy import SettingsProxy


class NetworkSDRInterfacePlugin(SDRPlugin):
    NETWORK_SDR_NAME = "Network SDR"  # Display text for device combo box
    rcv_index_changed = pyqtSignal(int, int)  # int arguments are just for compatibility with native and grc backend
    show_proto_sniff_dialog_clicked = pyqtSignal()
    sending_status_changed = pyqtSignal(bool)
    sending_stop_requested = pyqtSignal()
    current_send_message_changed = pyqtSignal(int)

    class MyTCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            received = self.request.recv(4096)
            self.data = received
            while received:
                received = self.request.recv(4096)
                self.data += received
            # print("{} wrote:".format(self.client_address[0]))
            # print(self.data)
            if hasattr(self.server, "received_bits"):
                self.server.received_bits.append(NetworkSDRInterfacePlugin.bytearray_to_bit_str(self.data))
            else:
                received = np.frombuffer(self.data, dtype=np.complex64)
                self.server.receive_buffer[
                self.server.current_receive_index:self.server.current_receive_index + len(received)] = received
                self.server.current_receive_index += len(received)

    def __init__(self, raw_mode=False, resume_on_full_receive_buffer=False, spectrum=False):
        """

        :param raw_mode: If true, sending and receiving raw samples if false bits are received/sent
        """
        super().__init__(name="NetworkSDRInterface")
        self.client_ip = self.qsettings.value("client_ip", defaultValue="127.0.0.1", type=str)
        self.server_ip = ""

        self.client_port = self.qsettings.value("client_port", defaultValue=2222, type=int)
        self.server_port = self.qsettings.value("server_port", defaultValue=4444, type=int)

        self.receive_check_timer = QTimer()
        self.receive_check_timer.setInterval(250)
        # need to make the connect for the time in constructor, as create connects is called elsewhere in base class
        self.receive_check_timer.timeout.connect(self.__emit_rcv_index_changed)

        self.is_in_spectrum_mode = spectrum
        self.resume_on_full_receive_buffer = resume_on_full_receive_buffer
        self.__is_sending = False
        self.__sending_interrupt_requested = False

        self.sending_repeats = 1  # only used in raw mode
        self.current_sent_sample = 0
        self.current_sending_repeat = 0

        self.raw_mode = raw_mode
        if self.raw_mode:
            num_samples = SettingsProxy.get_receive_buffer_size(self.resume_on_full_receive_buffer,
                                                                self.is_in_spectrum_mode)
            try:
                self.receive_buffer = np.zeros(num_samples, dtype=np.complex64, order='C')
            except MemoryError:
                logger.warning("Could not allocate buffer with {0:d} samples, trying less...")
                self.receive_buffer = np.zeros(num_samples // 2, dtype=np.complex64, order='C')
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
    def received_data(self):
        if self.raw_mode:
            return self.receive_buffer[:self.current_receive_index]
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
        if hasattr(self.server, "current_receive_index"):
            self.server.current_receive_index = value
        else:
            pass

    def free_data(self):
        if self.raw_mode:
            self.receive_buffer = np.empty(0)
        else:
            self.received_bits[:] = []

    def create_connects(self):
        self.settings_frame.lineEditClientIP.setText(self.client_ip)
        self.settings_frame.spinBoxClientPort.setValue(self.client_port)
        self.settings_frame.spinBoxServerPort.setValue(self.server_port)

        self.settings_frame.lineEditClientIP.editingFinished.connect(self.on_linedit_client_ip_editing_finished)
        self.settings_frame.lineEditServerIP.editingFinished.connect(self.on_linedit_server_ip_editing_finished)
        self.settings_frame.spinBoxClientPort.editingFinished.connect(self.on_spinbox_client_port_editing_finished)
        self.settings_frame.spinBoxServerPort.editingFinished.connect(self.on_spinbox_server_port_editing_finished)

        self.settings_frame.lOpenProtoSniffer.linkActivated.connect(self.on_lopenprotosniffer_link_activated)

    def start_tcp_server_for_receiving(self):
        self.server = socketserver.TCPServer((self.server_ip, self.server_port), self.MyTCPHandler)
        if self.raw_mode:
            self.server.receive_buffer = self.receive_buffer
            self.server.current_receive_index = 0
        else:
            self.server.received_bits = self.received_bits

        self.receive_check_timer.start()

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop_tcp_server(self):
        self.receive_check_timer.stop()
        if hasattr(self, "server"):
            logger.debug("Shutdown TCP server")
            self.server.shutdown()
            self.server.server_close()
        if hasattr(self, "server_thread"):
            self.server_thread.join()

    def send_data(self, data) -> str:
        # Create a socket (SOCK_STREAM means a TCP socket)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Connect to server and send data
                sock.connect((self.client_ip, self.client_port))
                sock.sendall(data)
                return ""
        except Exception as e:
            return str(e)

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
                logger.debug("Sent message {0}/{1}".format(i + 1, len(messages)))
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
        self.sending_thread = threading.Thread(target=self.__send_messages, args=(messages, sample_rates))
        self.sending_thread.daemon = True
        self.sending_thread.start()

    def start_raw_sending_thread(self):
        self.__sending_interrupt_requested = False
        self.sending_thread = threading.Thread(target=self.send_raw_data,
                                               args=(self.samples_to_send, self.sending_repeats))
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
        return bytearray((int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)))

    def on_linedit_client_ip_editing_finished(self):
        ip = self.settings_frame.lineEditClientIP.text()
        self.client_ip = ip
        self.qsettings.setValue('client_ip', self.client_ip)

    def on_linedit_server_ip_editing_finished(self):
        # Does nothing, because field is disabled
        ip = self.settings_frame.lineEditServerIP.text()
        self.server_ip = ip
        self.qsettings.setValue('server_ip', self.server_ip)

    def on_spinbox_client_port_editing_finished(self):
        self.client_port = self.settings_frame.spinBoxClientPort.value()
        self.qsettings.setValue('client_port', str(self.client_port))

    def on_spinbox_server_port_editing_finished(self):
        self.server_port = self.settings_frame.spinBoxServerPort.value()
        self.qsettings.setValue('server_port', str(self.server_port))

    def __emit_rcv_index_changed(self):
        # for updating received bits in protocol sniffer
        if hasattr(self, "received_bits") and self.received_bits:
            self.rcv_index_changed.emit(0, 0)  # int arguments are just for compatibility with native and grc backend

    @pyqtSlot(str)
    def on_lopenprotosniffer_link_activated(self, link: str):
        if link == "open_proto_sniffer":
            self.show_proto_sniff_dialog_clicked.emit()
