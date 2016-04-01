import unittest

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import qApp, QMessageBox

import tests.startApp
from urh.controller.MainController import MainController
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer

app = tests.startApp.app


class ProtocolSnifferTest(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.bit_len = 250
        self.center = 0.0644
        self.noise = 0.0332
        self.tolerance = 5
        self.modulation_type = 0  # ASK

        self.sample_rate = 1e6
        self.freq = 433.92e6
        self.gain = 20
        self.bandwidth = 1e6
        self.device = "HackRF"

    def test_sniff(self):
        sniffer = ProtocolSniffer(self.bit_len, self.center, self.noise,
                                  self.tolerance, self.modulation_type,
                                  self.sample_rate, self.freq, self.gain,
                                  self.bandwidth, self.device)

        sniffer.sniff()

        timer = QTimer()
        timer.timeout.connect(self.__confirm_message_box)
        timer.start(100)

        while sniffer.rcv_thrd.isRunning():
            QTest.qWait(100)

        self.assertTrue(True)

    def __confirm_message_box(self):
        for w in qApp.topLevelWidgets():
            if type(w) == QMessageBox:
                QTest.keyClick(w, Qt.Key_Enter)
