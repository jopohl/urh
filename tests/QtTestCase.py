import os
import sys
import unittest

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.utils_testing import write_settings, get_path_for_data_file
from urh.controller.MainController import MainController

import faulthandler

faulthandler.enable()


class QtTestCase(unittest.TestCase):
    CLOSE_TIMEOUT = 10
    WAIT_TIMEOUT_BEFORE_NEW = 10
    SHOW = os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "show_gui"))

    @classmethod
    def setUpClass(cls):
        write_settings()
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)
        cls.app = None

    def setUp(self):
        self.form = MainController()
        if self.SHOW:
            self.form.show()

    def wait_before_new_file(self):
        QApplication.instance().processEvents()
        QTest.qWait(self.WAIT_TIMEOUT_BEFORE_NEW)

    def add_signal_to_form(self, filename: str):
        self.wait_before_new_file()
        self.form.add_signalfile(get_path_for_data_file(filename))

    def tearDown(self):
        if hasattr(self, "dialog"):
            self.dialog.close()
        if hasattr(self, "form"):
            self.form.close_all()
            if self.SHOW:
                self.form.close()
        QApplication.instance().processEvents()
        QTest.qWait(self.CLOSE_TIMEOUT)
