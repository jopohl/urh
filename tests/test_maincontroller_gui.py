import sys
import unittest

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import tests.utils_testing
from tests import utils_testing
from urh.controller.MainController import MainController

utils_testing.write_settings()


class TestMaincontrollerGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)

    def setUp(self):
        self.form = MainController()

    def tearDown(self):
        self.form.close_all()
        QApplication.instance().processEvents()
        QTest.qWait(1)

    def test_open_recent(self):
        # Ensure we have at least one recent action
        self.form.add_signalfile(tests.utils_testing.get_path_for_data_file("esaver.complex"))
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

        self.form.recentFileActionList[0].trigger()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 2)

    def test_update_decodings(self):
        self.form.update_decodings()
        self.assertTrue(True)

    def test_options_changed(self):
        self.form.add_signalfile(tests.utils_testing.get_path_for_data_file("esaver.complex"))
        self.form.on_options_changed({"rel_symbol_length": 0, "show_pause_as_time": True, "default_view": 0})
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.currentIndex(), 0)
