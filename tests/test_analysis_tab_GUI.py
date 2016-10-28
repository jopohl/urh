import unittest

import tests.startApp
from urh.controller.MainController import MainController

app = tests.startApp.app


class TestAnalysisTabGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.form.add_signalfile("./data/fsk.complex")
        self.cfc = self.form.compare_frame_controller

    def test_analyze_button(self):
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)