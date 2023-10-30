import time
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection

import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QVBoxLayout,
    QGraphicsView,
    QPushButton,
    QGraphicsScene,
    QLabel,
)

from urh.signalprocessing.Spectrogram import Spectrogram


def generate_data(connection: Connection, num_samples=32768):
    frequency = 0.1
    divisor = 200
    pos = 0
    while True:
        result = np.zeros(num_samples, dtype=np.complex64)
        result.real = np.cos(2 * np.pi * frequency * np.arange(pos, pos + num_samples))
        result.imag = np.sin(2 * np.pi * frequency * np.arange(pos, pos + num_samples))
        pos += num_samples
        if pos / num_samples >= divisor:
            frequency *= 2
            if frequency >= 1:
                frequency = 0.1
            pos = 0
        connection.send(result)


def go():
    global graphic_view, status_label
    data_parent, data_child = Pipe(duplex=False)
    receiver = Process(target=generate_data, args=(data_child,))
    receiver.daemon = True
    receiver.start()

    scene = QGraphicsScene()
    graphic_view.setScene(scene)
    scene.setSceneRect(0, 0, 1024, 1024)

    x_pos = 0
    y_pos = 0
    t = time.time()
    while True:
        speed = time.time()
        data = data_parent.recv()
        spectrogram = Spectrogram(data)
        pixmap = QPixmap.fromImage(spectrogram.create_spectrogram_image(transpose=True))

        scene.setSceneRect(scene.sceneRect().adjusted(0, 0, 0, pixmap.height()))
        item = scene.addPixmap(pixmap)
        item.setPos(x_pos, y_pos)
        y_pos += pixmap.height()
        graphic_view.fitInView(scene.sceneRect())
        status_label.setText(
            "Height: {0:.0f} // Speed: {1:.2f}  // Total Time: {2:.2f}".format(
                scene.sceneRect().height(), 1 / (time.time() - speed), time.time() - t
            )
        )
        QApplication.instance().processEvents()


if __name__ == "__main__":
    global graphic_view, status_label
    app = QApplication(["spectrum"])
    widget = QFrame()
    layout = QVBoxLayout()
    graphic_view = QGraphicsView()
    layout.addWidget(graphic_view)
    status_label = QLabel()
    layout.addWidget(status_label)
    btn = QPushButton("Go")
    layout.addWidget(btn)
    btn.clicked.connect(go)
    widget.setLayout(layout)

    widget.showMaximized()
    app.exec_()
