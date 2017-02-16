import unittest

from PyQt5.QtCore import QPoint
from PyQt5.QtTest import QTest

import tests.utils_testing
from urh.controller.MainController import MainController
from tests.utils_testing import get_path_for_data_file

app = tests.utils_testing.app


class TestSignalTabGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.frame = self.form.signal_tab_controller.signal_frames[0]

    def test_close_all(self):
        self.form.close_all()
        QTest.qWait(50)
        self.assertEqual(self.form.signal_tab_controller.num_signals, 0)

        # Add a bunch of signals
        num_signals = 10
        for _ in range(num_signals):
            self.form.add_signalfile(get_path_for_data_file("esaver.complex"))

        self.assertEqual(self.form.signal_tab_controller.num_signals, num_signals)

        self.form.close_all()
        QTest.qWait(50)

        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        self.assertEqual(self.form.signal_tab_controller.num_signals, 1)

    def test_zoom(self):
        x_zoom = self.frame.ui.spinBoxXZoom.value()
        self.assertEqual(x_zoom, 100)

        for _ in range(10):
            self.frame.ui.gvSignal.zoom(1.01)
            self.assertGreater(self.frame.ui.spinBoxXZoom.value(), x_zoom)
            x_zoom = self.frame.ui.spinBoxXZoom.value()

        for _ in range(10):
            self.frame.ui.gvSignal.zoom(0.99)
            self.assertLess(self.frame.ui.spinBoxXZoom.value(), x_zoom)
            x_zoom = self.frame.ui.spinBoxXZoom.value()

        samples_in_view = self.frame.ui.lSamplesInView.text()
        self.frame.ui.spinBoxXZoom.setValue(self.frame.ui.spinBoxXZoom.value() + 400)
        self.assertNotEqual(samples_in_view, self.frame.ui.lSamplesInView.text())

    def test_load_proto(self):
        self.form.add_files([get_path_for_data_file("protocol.proto")])
        self.assertEqual(self.form.signal_tab_controller.signal_frames[1].ui.lSignalTyp.text(), "Protocol (*.proto)")

    def test_graphic_view_selection(self):
        self.frame.ui.gvSignal.selection_area.start = 0
        self.frame.ui.gvSignal.selection_area.end = 4000
        self.frame.ui.gvSignal.sel_area_start_end_changed.emit(0, 4000)

        self.assertEqual(self.frame.ui.lNumSelectedSamples.text(), "4000")

        noise_val = self.frame.ui.spinBoxNoiseTreshold.value()
        self.frame.ui.gvSignal.set_noise_clicked.emit()
        self.assertNotEqual(noise_val, self.frame.ui.spinBoxNoiseTreshold.value())

        self.frame.ui.spinBoxSelectionStart.setValue(300)
        self.assertEqual(self.frame.ui.gvSignal.selection_area.start, 300)
        self.frame.ui.spinBoxSelectionEnd.setValue(6000)
        self.assertEqual(self.frame.ui.gvSignal.selection_area.end, 6000)

    def test_graphic_view_zoom_to_selection(self):
        self.frame.ui.gvSignal.context_menu_position = QPoint(0, 0)
        menu = self.frame.ui.gvSignal.create_context_menu()
        self.assertTrue(self.frame.ui.gvSignal.selection_area.is_empty)
        self.assertIsNone(next((action for action in menu.actions() if action.text() == "Zoom selection"), None))

        self.frame.ui.gvSignal.selection_area.start = 1337
        self.frame.ui.gvSignal.selection_area.end = 4711
        self.frame.ui.gvSignal.sel_area_start_end_changed.emit(1337, 4711)

        menu = self.frame.ui.gvSignal.create_context_menu()
        self.assertFalse(self.frame.ui.gvSignal.selection_area.is_empty)
        zoom_action = next(action for action in menu.actions() if action.text() == "Zoom selection")
        zoom_action.trigger()
        self.assertEqual(self.frame.ui.spinBoxSelectionStart.value(), 1337)
        self.assertEqual(self.frame.ui.spinBoxSelectionEnd.value(), 4711)

    def test_show_hide_start_end(self):
        self.assertEqual(self.frame.ui.btnShowHideStartEnd.text(), "+")
        self.frame.ui.btnShowHideStartEnd.click()
        self.assertEqual(self.frame.ui.btnShowHideStartEnd.text(), "-")
