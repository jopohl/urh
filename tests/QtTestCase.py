import sys
import unittest

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
        QTest.qWait(10)
        time.sleep(0.01)

    def setUp(self):
        self.form = MainController()

    def add_signal_to_form(self, filename: str):
        QApplication.instance().processEvents()
        QTest.qWait(1)

        self.form.add_signalfile(get_path_for_data_file(filename))

        QApplication.instance().processEvents()
        QTest.qWait(1)

    def tearDown(self):
        QApplication.instance().processEvents()
        QTest.qWait(1)

        if hasattr(self, "dialog"):
            self.dialog.close()

        if hasattr(self, "form"):
            self.form.close_all()
            self.form.close()

        if hasattr(self, "signal"):
            try:
                self.signal.eliminate()
                self.signal.setParent(None)
                self.signal.deleteLater()
            except RuntimeError:
                pass  # Signal is already deleted, nice!

        QApplication.instance().processEvents()
        QTest.qWait(10)
        time.sleep(0.01)
