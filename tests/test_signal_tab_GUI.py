import unittest

from PyQt5.QtTest import QTest

import tests.utils_testing
from urh.controller.MainController import MainController
from tests.utils_testing import get_path_for_data_file
app = tests.utils_testing.app


class TestSignalTabGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()

    def test_close_all(self):
        # Add a bunch of signals
        NUM_SIGNALS = 10
        for _ in range(NUM_SIGNALS):
            self.form.add_signalfile(get_path_for_data_file("esaver.complex"))

        self.assertEqual(self.form.signal_tab_controller.num_signals, NUM_SIGNALS)

        self.form.close_all()
        QTest.qWait(1)
        self.assertEqual(self.form.signal_tab_controller.num_signals, 0)

        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        self.assertEqual(self.form.signal_tab_controller.num_signals, 1)

    def test_zoom(self):
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        frame = self.form.signal_tab_controller.signal_frames[0]
        x_zoom = frame.ui.spinBoxXZoom.value()
        self.assertEqual(x_zoom, 100)

        for _ in range(10):
            frame.ui.gvSignal.zoom(1.01)
            self.assertGreater(frame.ui.spinBoxXZoom.value(), x_zoom)
            x_zoom = frame.ui.spinBoxXZoom.value()

        for _ in range(10):
            frame.ui.gvSignal.zoom(0.99)
            self.assertLess(frame.ui.spinBoxXZoom.value(), x_zoom)
            x_zoom = frame.ui.spinBoxXZoom.value()

        samples_in_view = frame.ui.lSamplesInView.text()
        frame.ui.spinBoxXZoom.setValue(frame.ui.spinBoxXZoom.value() + 400)
        self.assertNotEqual(samples_in_view, frame.ui.lSamplesInView.text())

    def test_load_proto(self):
        self.form.add_files([get_path_for_data_file("protocol.proto")])
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].ui.lSignalTyp.text(), "Protocol (*.proto)")

    def test_graphic_view_selection(self):
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        frame = self.form.signal_tab_controller.signal_frames[0]

        frame.ui.gvSignal.selection_area.start = 0
        frame.ui.gvSignal.selection_area.end = 4000
        frame.ui.gvSignal.sel_area_start_end_changed.emit(0, 4000)

        self.assertEqual(frame.ui.lNumSelectedSamples.text(), "4000")

        noise_val = frame.ui.spinBoxNoiseTreshold.value()
        frame.ui.gvSignal.set_noise_clicked.emit()
        self.assertNotEqual(noise_val, frame.ui.spinBoxNoiseTreshold.value())

        frame.ui.spinBoxSelectionStart.setValue(300)
        self.assertEqual(frame.ui.gvSignal.selection_area.start, 300)
        frame.ui.spinBoxSelectionEnd.setValue(6000)
        self.assertEqual(frame.ui.gvSignal.selection_area.end, 6000)

    def test_show_hide_start_end(self):
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        frame = self.form.signal_tab_controller.signal_frames[0]

        self.assertEqual(frame.ui.btnShowHideStartEnd.text(), "+")
        frame.ui.btnShowHideStartEnd.click()
        self.assertEqual(frame.ui.btnShowHideStartEnd.text(), "-")
