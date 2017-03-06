import unittest

from PyQt5.QtTest import QTest

import tests.utils_testing
from urh.controller.MainController import MainController

app = tests.utils_testing.app


class TestMaincontrollerGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()

    def test_open_recent(self):
        self.form.add_signalfile(tests.utils_testing.get_path_for_data_file("esaver.complex"))
        app.processEvents()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)
        self.form.close_all()
        app.processEvents()
        QTest.qWait(10)
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 0)
        self.form.recentFileActionList[0].trigger()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

    def test_update_decodings(self):
        self.form.update_decodings()
        self.assertTrue(True)
