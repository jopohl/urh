import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import tests.startApp
from urh.controller.MainController import MainController

app = tests.startApp.app


class TestAnalysisTabGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.cfc = self.form.compare_frame_controller

    def test_analyze_button_fsk(self):
        self.form.add_signalfile("./data/fsk.complex")
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)

    def test_analyze_button_enocean(self):
        self.form.add_signalfile("./data/enocean.complex")
        w = self.form.signal_tab_controller.signal_frames[0].ui.spinBoxCenterOffset
        w.setValue(0)
        QTest.keyClick(w, Qt.Key_Enter)
        w = self.form.signal_tab_controller.signal_frames[0].ui.spinBoxNoiseTreshold
        w.setValue(0.0111)
        QTest.keyClick(w, Qt.Key_Enter)
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)