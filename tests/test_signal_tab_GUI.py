import os
import unittest

from PyQt5.QtCore import QDir
from PyQt5.QtCore import QPoint
from PyQt5.QtTest import QTest

import tests.utils_testing
from urh import constants
from urh.controller.MainController import MainController
from tests.utils_testing import get_path_for_data_file
from urh.util.Logger import logger

app = tests.utils_testing.get_app()


class TestSignalTabGUI(unittest.TestCase):
    def setUp(self):
        constants.SETTINGS.setValue("not_show_save_dialog", True)
        self.form = MainController()
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.frame = self.form.signal_tab_controller.signal_frames[0]
        self.frame.signal.noise_threshold = 0.0023
        self.frame.signal.qad_center = 0.3817
        self.frame.signal.bit_len = 84

    def test_close_all(self):
        self.form.close_all()
        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)

        # Add a bunch of signals
        num_frames = 5
        for _ in range(num_frames):
            tests.utils_testing.short_wait()
            self.form.add_signalfile(get_path_for_data_file("esaver.complex"))

        self.assertEqual(self.form.signal_tab_controller.num_frames, num_frames)

        self.form.close_all()

        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)

    def test_zoom(self):
        tests.utils_testing.short_wait()
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

    def test_apply_to_all(self):
        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        frame2 = self.form.signal_tab_controller.signal_frames[1]

        self.frame.ui.spinBoxInfoLen.setValue(42)
        self.frame.ui.spinBoxInfoLen.editingFinished.emit()

        self.frame.ui.spinBoxCenterOffset.setValue(0.1)
        self.frame.ui.spinBoxCenterOffset.editingFinished.emit()

        self.frame.ui.spinBoxNoiseTreshold.setValue(0.5)
        self.frame.ui.spinBoxNoiseTreshold.editingFinished.emit()

        self.frame.ui.spinBoxTolerance.setValue(10)
        self.frame.ui.spinBoxTolerance.editingFinished.emit()

        self.frame.apply_to_all_clicked.emit(self.frame.signal)

        self.assertEqual(42, frame2.ui.spinBoxInfoLen.value())
        self.assertEqual(0.1, frame2.ui.spinBoxCenterOffset.value())
        self.assertEqual(0.5, frame2.ui.spinBoxNoiseTreshold.value())
        self.assertEqual(10, frame2.ui.spinBoxTolerance.value())

    def test_save_all(self):
        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        frame2 = self.form.signal_tab_controller.signal_frames[1]

        self.frame.signal.changed = True
        self.frame.signal.filename = os.path.join(QDir.tempPath(), "sig1.complex")

        frame2.signal.changed = True
        frame2.signal.filename = os.path.join(QDir.tempPath(), "sig2.complex")

        self.assertFalse(os.path.isfile(self.frame.signal.filename))
        self.assertFalse(os.path.isfile(frame2.signal.filename))

        self.form.signal_tab_controller.save_all()

        self.assertTrue(os.path.isfile(self.frame.signal.filename))
        self.assertTrue(os.path.isfile(frame2.signal.filename))

        os.remove(self.frame.signal.filename)
        os.remove(frame2.signal.filename)

    def test_crop_and_save_signal(self):
        self.frame.ui.gvSignal.selection_area.end = 4000
        self.frame.ui.gvSignal.selection_area.start = 1000

        self.assertEqual(self.frame.ui.gvSignal.selection_area.end, 4000)
        self.assertEqual(self.frame.ui.gvSignal.selection_area.width, 3000)
        self.frame.ui.gvSignal.sel_area_start_end_changed.emit(1000, 4000)

        self.frame.ui.gvSignal.on_crop_action_triggered()
        self.assertEqual(self.frame.signal.num_samples, 3000)
        self.assertTrue(self.frame.signal.changed)

        self.frame.signal.filename = os.path.join(QDir.tempPath(), "sig.complex")
        if os.path.isfile(self.frame.signal.filename):
            os.remove(self.frame.signal.filename)

        self.assertFalse(os.path.isfile(self.frame.signal.filename))
        self.frame.ui.btnSaveSignal.click()
        self.form.close_signal_frame(self.frame)
        tests.utils_testing.short_wait()
        self.form.add_signalfile(os.path.join(QDir.tempPath(), "sig.complex"))
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].signal.num_samples, 3000)
        os.remove(os.path.join(QDir.tempPath(), "sig.complex"))

    def test_selection_sync(self):
        self.frame.ui.gvSignal.selection_area.end = 128440
        self.frame.ui.gvSignal.selection_area.start = 89383
        self.frame.ui.gvSignal.sel_area_start_end_changed.emit(89383, 128440)
        tests.utils_testing.short_wait()
        self.assertEqual(self.frame.proto_analyzer.messages[0].plain_bits_str, self.frame.ui.txtEdProto.selected_text)
        self.frame.ui.txtEdProto.show_proto_clicked.emit()
        tests.utils_testing.short_wait()
        self.assertAlmostEqual((128440 - 89383) / 1000000,
                               (self.frame.ui.gvSignal.view_rect().width()) / 1000000, places=1)

    def test_show_demod_view(self):
        self.assertTrue(self.frame.ui.gvLegend.isHidden())
        self.frame.ui.cbSignalView.setCurrentIndex(1)
        self.assertFalse(self.frame.ui.gvLegend.isHidden())

    def test_auto_detect_button(self):
        self.assertTrue(self.frame.ui.btnAutoDetect.isChecked())
        self.frame.ui.btnAutoDetect.click()
        self.assertFalse(self.frame.ui.btnAutoDetect.isChecked())
