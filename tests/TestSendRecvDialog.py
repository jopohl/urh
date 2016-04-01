import unittest

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import qApp, QMessageBox

import tests.startApp
from urh.controller.MainController import MainController
from urh.controller.SendRecvDialogController import SendRecvDialogController, Mode

app = tests.startApp.app


class TestSendRecvDialog(unittest.TestCase):
    def setUp(self):
        self.form = MainController()

    def test_recv(self):
        rcv_dialog = SendRecvDialogController(433e6, 1e6, 500e3, 20, "USRP", Mode.receive, parent = self.form)
        rcv_dialog.ui.btnStart.click()
        QTest.qWait(100)

        timer = QTimer()
        timer.timeout.connect(self.__confirm_message_box)
        timer.start(100)

        while rcv_dialog.device_thread.isRunning():
            QTest.qWait(100)

        self.assertTrue(True)

    def __confirm_message_box(self):
        for w in qApp.topLevelWidgets():
            if type(w) == QMessageBox:
                QTest.keyClick(w, Qt.Key_Enter)
