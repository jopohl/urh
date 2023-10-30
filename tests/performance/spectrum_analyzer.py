import socket
from multiprocessing import Process

import numpy as np
from PyQt5.QtWidgets import QApplication

from urh import settings
from urh.controller.MainController import MainController
from urh.controller.dialogs.SpectrumDialogController import SpectrumDialogController
from urh.util import util
from urh.util.ProjectManager import ProjectManager


def send_data(port):
    num_samples = settings.SPECTRUM_BUFFER_SIZE
    frequency = 0.1
    divisor = 200
    pos = 0
    while True:
        sock = open_socket(port)
        result = np.zeros(num_samples, dtype=np.complex64)
        result.real = np.cos(2 * np.pi * frequency * np.arange(pos, pos + num_samples))
        result.imag = np.sin(2 * np.pi * frequency * np.arange(pos, pos + num_samples))
        pos += num_samples
        if pos / num_samples >= divisor:
            frequency *= 2
            if frequency >= 1:
                frequency = 0.1
            pos = 0
        sock.sendall(result.tostring())
        close_socket(sock)


def open_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    sock.connect(("127.0.0.1", port))
    return sock


def close_socket(sock):
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


if __name__ == "__main__":
    app = QApplication(["test"])
    main = MainController()
    port = util.get_free_port()
    dialog = SpectrumDialogController(ProjectManager(main))
    dialog.showMaximized()
    dialog.ui.cbDevice.setCurrentText("Network SDR")
    dialog.device.set_server_port(port)
    dialog.ui.btnStart.click()

    p = Process(target=send_data, args=(port,))
    p.daemon = True
    p.start()

    num_samples = 32768
    frequency = 0.1
    divisor = 200
    pos = 0
    app.exec_()
    p.terminate()
    p.join()
