import sys
import unittest

import gc
import sip
import time
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.utils_testing import write_settings, get_path_for_data_file
from urh.controller.MainController import MainController


class QtTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        write_settings()
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)
        del cls.app
        QTest.qSleep(100)

    def setUp(self):
        self.form = MainController()

    def add_signal_to_form(self, filename: str):
        self.form.add_signalfile(get_path_for_data_file(filename))

    def tearDown(self):
        if hasattr(self, "dialog"):
            self.dialog.close()
            self.dialog.setParent(None)
            sip.delete(self.dialog)
            del self.dialog

        if hasattr(self, "form"):
            self.form.close_all()
            self.form.setParent(None)
            sip.delete(self.form)
            del self.form

        QApplication.instance().processEvents()
        QTest.qWait(10)
        QTest.qSleep(10)
        gc.collect()
