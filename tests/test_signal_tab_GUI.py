import unittest

from PyQt5.QtTest import QTest

import tests.startApp
from urh.controller.MainController import MainController

app = tests.startApp.app


class TestSignalTabGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()

    def test_close_all(self):
        # Add a bunch of signals
        NUM_SIGNALS = 10
        for _ in range(NUM_SIGNALS):
            self.form.add_signalfile("./data/esaver.complex")

        self.assertEqual(self.form.signal_tab_controller.num_signals, NUM_SIGNALS)

        self.form.close_all()
        QTest.qWait(1)
        self.assertEqual(self.form.signal_tab_controller.num_signals, 0)

        self.form.add_signalfile("./data/ask.complex")
        self.assertEqual(self.form.signal_tab_controller.num_signals, 1)
