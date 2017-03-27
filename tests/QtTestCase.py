import sys
import unittest

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.utils_testing import write_settings, get_path_for_data_file
from urh.controller.MainController import MainController


class QtTestCase(unittest.TestCase):
    CLOSE_TIMEOUT = 50

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
        QApplication.instance().processEvents()
        self.form = MainController()
        QApplication.instance().processEvents()
        QTest.qWait(10)

    def add_signal_to_form(self, filename: str):
        QApplication.instance().processEvents()
        QTest.qWait(10)
        self.form.add_signalfile(get_path_for_data_file(filename))

    def tearDown(self):
        if hasattr(self, "dialog"):
            self.dialog.close()
            self.dialog.setParent(None)
            self.dialog.deleteLater()
            sip.delete(self.dialog)
            del self.dialog

        if hasattr(self, "form"):
            self.form.close_all()
            self.form.setParent(None)
            self.form.deleteLater()
            sip.delete(self.form)
            del self.form

        QApplication.processEvents()
        QTest.qWait(self.CLOSE_TIMEOUT)
