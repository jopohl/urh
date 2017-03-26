import sys
import unittest

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests import utils_testing
from tests.utils_testing import get_path_for_data_file
from urh.controller.SignalDetailsController import SignalDetailsController
from urh.signalprocessing.Signal import Signal
from urh.util.Formatter import Formatter

utils_testing.write_settings()


class TestSignalDetailsGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)

    def setUp(self):
        self.signal = Signal(get_path_for_data_file("esaver.complex"), "test")
        self.signal.sample_rate = 2e6
        self.dialog = SignalDetailsController(self.signal)

    def tearDown(self):
        self.dialog.close()
        QApplication.instance().processEvents()
        QTest.qWait(1)

    def test_set_sample_rate(self):
        self.assertEqual(Formatter.science_time(self.signal.num_samples / self.signal.sample_rate),
                         self.dialog.ui.lDuration.text())

        self.dialog.ui.dsb_sample_rate.setValue(5e6)
        self.assertEqual(self.signal.sample_rate, 5e6)
        self.assertEqual(Formatter.science_time(self.signal.num_samples / self.signal.sample_rate),
                         self.dialog.ui.lDuration.text())

