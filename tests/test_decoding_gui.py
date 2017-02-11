import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtTest import QTest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh.controller.DecoderWidgetController import DecoderWidgetController
from urh.controller.MainController import MainController

app = tests.utils_testing.app


class TestDecodingGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.signal = self.form.signal_tab_controller.signal_frames[0].signal
        self.dialog = DecoderWidgetController(decodings=self.form.compare_frame_controller.decodings,
                                              signals=[self.signal],
                                              project_manager=self.form.project_manager)

    def test_edit_decoding(self):
        self.dialog.ui.combobox_decodings.setCurrentIndex(1)  # NRZI
        self.assertEqual(self.dialog.ui.decoderchain.count(), 1)  # One Invert

    def test_select_items(self):
        for i in range(0, self.dialog.ui.basefunctions.count()):
            self.dialog.ui.basefunctions.setCurrentRow(i)
            self.assertIn(self.dialog.ui.basefunctions.currentItem().text(), self.dialog.ui.info.text())

        for i in range(0, self.dialog.ui.additionalfunctions.count()):
            self.dialog.ui.additionalfunctions.setCurrentRow(i)
            self.assertIn(self.dialog.ui.additionalfunctions.currentItem().text(), self.dialog.ui.info.text())
