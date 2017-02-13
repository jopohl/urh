import unittest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh.controller.SignalDetailsController import SignalDetailsController
from urh.signalprocessing.Signal import Signal
from urh.util.Formatter import Formatter

app = tests.utils_testing.app


class TestSignalDetailsGUI(unittest.TestCase):
    def setUp(self):
        self.signal = Signal(get_path_for_data_file("esaver.complex"), "test")
        self.signal.sample_rate = 2e6
        self.dialog = SignalDetailsController(self.signal)

    def test_set_sample_rate(self):
        self.assertEqual(Formatter.science_time(self.signal.num_samples / self.signal.sample_rate),
                         self.dialog.ui.lDuration.text())

        self.dialog.ui.dsb_sample_rate.setValue(5e6)
        self.assertEqual(self.signal.sample_rate, 5e6)
        self.assertEqual(Formatter.science_time(self.signal.num_samples / self.signal.sample_rate),
                         self.dialog.ui.lDuration.text())

