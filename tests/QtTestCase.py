import unittest

import sys

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.utils_testing import write_settings
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

    def setUp(self):
        self.form = MainController()

    def tearDown(self):
        self.form.close_all()
        self.form.close()
        self.form.setParent(None)
        sip.delete(self.form)
        QApplication.instance().processEvents()
        QTest.qWait(25)
