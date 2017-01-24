import socketserver
import threading

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
import socket

from urh.plugins.Plugin import SDRPlugin


class NetworkSDRInterfacePlugin(SDRPlugin):
    NETWORK_SDR_NAME = "Network SDR"  # Display text for device combo box

    class MyTCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            self.data = self.request.recv(1024)
            #print("{} wrote:".format(self.client_address[0]))
            #print(self.data)
            self.server.received_bits.append(NetworkSDRInterfacePlugin.bytearray_to_bit_str(self.data))
            print(self.server.received_bits)

    def __init__(self):
        super().__init__(name="NetworkSDRInterface")
        self.client_ip = self.qsettings.value("client_ip", defaultValue="127.0.0.1", type=str)
        self.server_ip = self.qsettings.value("server_ip", defaultValue="127.0.0.1", type=str)

        self.client_port = self.qsettings.value("client_port", defaultValue=1338, type=int)
        self.server_port = self.qsettings.value("server_port", defaultValue=1337, type=int)

        self.received_bits = []

    def create_connects(self):
        ip_regex = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        self.settings_frame.lineEditClientIP.setValidator(QRegExpValidator(QRegExp(ip_regex)))
        self.settings_frame.lineEditServerIP.setValidator(QRegExpValidator(QRegExp(ip_regex)))

        self.settings_frame.lineEditClientIP.setText(self.client_ip)
        self.settings_frame.lineEditServerIP.setText(self.server_ip)
        self.settings_frame.spinBoxClientPort.setValue(self.client_port)
        self.settings_frame.spinBoxServerPort.setValue(self.server_port)

        self.settings_frame.lineEditClientIP.editingFinished.connect(self.on_linedit_client_ip_editing_finished)
        self.settings_frame.lineEditServerIP.editingFinished.connect(self.on_linedit_server_ip_editing_finished)
        self.settings_frame.spinBoxClientPort.editingFinished.connect(self.on_spinbox_client_port_editing_finished)
        self.settings_frame.spinBoxServerPort.editingFinished.connect(self.on_spinbox_server_port_editing_finished)

    def start_tcp_server_for_receiving(self):
        self.server = socketserver.TCPServer((self.server_ip, self.server_port), self.MyTCPHandler,
                                             bind_and_activate=False)
        self.server.received_bits = self.received_bits

        self.server.allow_reuse_address = True  # allow reusing addresses if the server is stopped and started again
        self.server.server_bind()      # only necessary, because we disabled bind_and_activate above
        self.server.server_activate()  # only necessary, because we disabled bind_and_activate above

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop_tcp_server(self):
        if hasattr(self, "server"):
            self.server.shutdown()
        if hasattr(self, "server_thread"):
            self.server_thread.join()


    def send_data(self, data:bytearray):
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((self.client_ip, self.client_port))
            sock.sendall(data)

    @staticmethod
    def bytearray_to_bit_str(arr: bytearray) -> str:
        return "".join("{:08b}".format(a) for a in arr)

    @staticmethod
    def bit_str_to_bytearray(bits: str) -> bytearray:
        bits += "0" * ((8 - len(bits) % 8) % 8)
        return bytearray((int(bits[i:i+8], 2) for i in range(0, len(bits), 8)))

    @staticmethod
    def ip_is_valid(ip: str):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def on_linedit_client_ip_editing_finished(self):
        ip = self.settings_frame.lineEditClientIP.text()
        if self.ip_is_valid(ip):
            self.client_ip = ip
            self.qsettings.setValue('client_ip', self.client_ip)

    def on_linedit_server_ip_editing_finished(self):
        ip = self.settings_frame.lineEditServerIP.text()
        if self.ip_is_valid(ip):
            self.server_ip = ip
            self.qsettings.setValue('server_ip', self.server_ip)

    def on_spinbox_client_port_editing_finished(self):
        self.client_port = self.settings_frame.spinBoxClientPort.value()
        self.qsettings.setValue('client_port', str(self.client_port))

    def on_spinbox_server_port_editing_finished(self):
        self.server_port = self.settings_frame.spinBoxServerPort.value()
        self.qsettings.setValue('server_port', str(self.server_port))