import os

from PyQt5.QtCore import QDir, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh.controller.MainController import MainController
from urh.signalprocessing.Participant import Participant


class TestSignalTabGUI(QtTestCase):
    def test_close_project(self):
        self.add_signal_to_form("esaver.complex16s")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        self.form.close_all_files()

        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)

        # Add a bunch of signals
        num_frames = 5
        for _ in range(num_frames):
            self.add_signal_to_form("esaver.complex16s")

        self.assertEqual(self.form.signal_tab_controller.num_frames, num_frames)

        self.form.close_project()

        self.add_signal_to_form("ask.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)

    def test_zoom(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        QApplication.instance().processEvents()
        x_zoom = frame.ui.spinBoxXZoom.value()
        self.assertIn(x_zoom, range(100, 111))

        for _ in range(10):
            frame.ui.gvSignal.zoom(1.1)
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
        self.form.add_files([get_path_for_data_file("protocol.proto.xml")])
        self.assertEqual(
            self.form.signal_tab_controller.signal_frames[0].ui.lSignalTyp.text(),
            "Protocol",
        )

    def test_graphic_view_selection(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        frame.ui.gvSignal.selection_area.start = 0
        frame.ui.gvSignal.selection_area.end = 4000
        frame.ui.gvSignal.sel_area_start_end_changed.emit(0, 4000)

        self.assertEqual(frame.ui.lNumSelectedSamples.text(), "4000")

        frame.ui.spinBoxNoiseTreshold.setValue(1)
        noise_val = frame.ui.spinBoxNoiseTreshold.value()
        frame.ui.gvSignal.set_noise_clicked.emit()
        self.assertNotEqual(noise_val, frame.ui.spinBoxNoiseTreshold.value())

        frame.ui.spinBoxSelectionStart.setValue(300)
        self.assertEqual(frame.ui.gvSignal.selection_area.start, 300)
        frame.ui.spinBoxSelectionEnd.setValue(6000)
        self.assertEqual(frame.ui.gvSignal.selection_area.end, 6000)

    def test_graphic_view_zoom_to_selection(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        frame.ui.gvSignal.context_menu_position = QPoint(0, 0)
        menu = frame.ui.gvSignal.create_context_menu()
        self.assertTrue(frame.ui.gvSignal.selection_area.is_empty)
        self.assertIsNone(
            next(
                (
                    action
                    for action in menu.actions()
                    if action.text() == "Zoom selection"
                ),
                None,
            )
        )

        frame.ui.gvSignal.selection_area.start = 1337
        frame.ui.gvSignal.selection_area.end = 4711
        frame.ui.gvSignal.sel_area_start_end_changed.emit(1337, 4711)

        menu = frame.ui.gvSignal.create_context_menu()
        self.assertFalse(frame.ui.gvSignal.selection_area.is_empty)
        zoom_action = next(
            action for action in menu.actions() if action.text() == "Zoom selection"
        )
        zoom_action.trigger()
        self.assertEqual(frame.ui.spinBoxSelectionStart.value(), 1337)
        self.assertEqual(frame.ui.spinBoxSelectionEnd.value(), 4711)

    def test_show_hide_start_end(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        self.assertFalse(frame.ui.btnShowHideStartEnd.isChecked())
        frame.ui.btnShowHideStartEnd.click()
        self.assertTrue(frame.ui.btnShowHideStartEnd.isChecked())

    def test_apply_to_all(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        self.add_signal_to_form("ask.complex")
        frame2 = self.form.signal_tab_controller.signal_frames[1]

        frame.ui.spinBoxSamplesPerSymbol.setValue(42)
        frame.ui.spinBoxSamplesPerSymbol.editingFinished.emit()

        frame.ui.spinBoxCenterOffset.setValue(0.1)
        frame.ui.spinBoxCenterOffset.editingFinished.emit()

        frame.ui.spinBoxNoiseTreshold.setValue(0.5)
        frame.ui.spinBoxNoiseTreshold.editingFinished.emit()

        frame.ui.spinBoxTolerance.setValue(10)
        frame.ui.spinBoxTolerance.editingFinished.emit()

        frame.signal.pause_threshold = 42
        frame.signal.message_length_divisor = 10

        frame.apply_to_all_clicked.emit(frame.signal)

        self.assertEqual(42, frame2.ui.spinBoxSamplesPerSymbol.value())
        self.assertEqual(0.1, frame2.ui.spinBoxCenterOffset.value())
        self.assertEqual(0.5, frame2.ui.spinBoxNoiseTreshold.value())
        self.assertEqual(10, frame2.ui.spinBoxTolerance.value())
        self.assertEqual(42, frame2.signal.pause_threshold)
        self.assertEqual(10, frame2.signal.message_length_divisor)

    def test_save_all(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        self.add_signal_to_form("ask.complex")
        frame2 = self.form.signal_tab_controller.signal_frames[1]

        frame.signal.changed = True
        frame.signal.filename = os.path.join(QDir.tempPath(), "sig1.complex")

        frame2.signal.changed = True
        frame2.signal.filename = os.path.join(QDir.tempPath(), "sig2.complex")

        self.assertFalse(os.path.isfile(frame.signal.filename))
        self.assertFalse(os.path.isfile(frame2.signal.filename))

        self.form.signal_tab_controller.save_all()

        self.assertTrue(os.path.isfile(frame.signal.filename))
        self.assertTrue(os.path.isfile(frame2.signal.filename))

        os.remove(frame.signal.filename)
        os.remove(frame2.signal.filename)

    def test_crop_and_save_signal(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        frame.ui.gvSignal.selection_area.end = 4000
        frame.ui.gvSignal.selection_area.start = 1000

        self.assertEqual(frame.ui.gvSignal.selection_area.end, 4000)
        self.assertEqual(frame.ui.gvSignal.selection_area.width, 3000)
        frame.ui.gvSignal.sel_area_start_end_changed.emit(1000, 4000)

        frame.ui.gvSignal.on_crop_action_triggered()
        self.assertEqual(frame.signal.num_samples, 3000)
        self.assertTrue(frame.signal.changed)

        frame.signal.filename = os.path.join(QDir.tempPath(), "sig.complex")
        if os.path.isfile(frame.signal.filename):
            os.remove(frame.signal.filename)

        self.assertFalse(os.path.isfile(frame.signal.filename))
        frame.ui.btnSaveSignal.click()
        self.form.close_signal_frame(frame)
        self.add_signal_to_form(os.path.join(QDir.tempPath(), "sig.complex"))
        self.assertEqual(
            self.form.signal_tab_controller.signal_frames[0].signal.num_samples, 3000
        )
        os.remove(os.path.join(QDir.tempPath(), "sig.complex"))

    def test_selection_sync(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        frame.ui.cbProtoView.setCurrentIndex(0)  # set to bit view
        frame.ui.gvSignal.selection_area.end = 128440
        frame.ui.gvSignal.selection_area.start = 89383
        frame.ui.gvSignal.sel_area_start_end_changed.emit(89383, 128440)
        QApplication.instance().processEvents()
        QTest.qWait(100)
        self.assertEqual(
            frame.proto_analyzer.messages[0].plain_bits_str,
            frame.ui.txtEdProto.selected_text.strip(),
        )
        frame.ui.txtEdProto.show_proto_clicked.emit()
        QApplication.instance().processEvents()
        self.assertAlmostEqual(
            (128440 - 89383) / 1000000,
            (frame.ui.gvSignal.view_rect().width()) / 1000000,
            places=1,
        )

    def test_auto_detect_button(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        frame.ui.btnAutoDetect.click()

    def test_create_new_signal(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        start, end = 400, 8568
        frame.ui.gvSignal.selection_area.end = end
        frame.ui.gvSignal.selection_area.start = start

        self.assertEqual(frame.ui.gvSignal.selection_area.end, end)
        self.assertEqual(frame.ui.gvSignal.selection_area.width, end - start)
        frame.ui.gvSignal.sel_area_start_end_changed.emit(start, end)

        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        frame.ui.gvSignal.on_create_action_triggered()
        QApplication.instance().processEvents()

        self.assertEqual(self.form.signal_tab_controller.num_frames, 2)
        self.assertEqual(
            self.form.signal_tab_controller.signal_frames[1].signal.num_samples,
            end - start,
        )

    def test_demodulated_view(self):
        self.add_signal_to_form("esaver.complex16s")
        frame = self.form.signal_tab_controller.signal_frames[0]
        frame.ui.cbSignalView.setCurrentIndex(1)
        QApplication.instance().processEvents()
        self.assertEqual(frame.ui.gvSignal.scene_type, 1)

    def test_context_menu_text_edit_protocol_view(self):
        self.add_signal_to_form("esaver.complex16s")
        self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.setCurrentIndex(
            2
        )
        text_edit = self.form.signal_tab_controller.signal_frames[0].ui.txtEdProto

        menu = text_edit.create_context_menu()
        line_wrap_action = next(
            action for action in menu.actions() if action.text().startswith("Linewrap")
        )
        checked = line_wrap_action.isChecked()
        line_wrap_action.trigger()

        menu = text_edit.create_context_menu()
        line_wrap_action = next(
            action for action in menu.actions() if action.text().startswith("Linewrap")
        )
        self.assertNotEqual(checked, line_wrap_action.isChecked())

        self.assertEqual(
            len(
                [action for action in menu.actions() if action.text() == "Participant"]
            ),
            0,
        )
        self.form.project_manager.participants.append(Participant("Alice", "A"))
        text_edit.selectAll()
        menu = text_edit.create_context_menu()
        self.assertEqual(
            len(
                [action for action in menu.actions() if action.text() == "Participant"]
            ),
            1,
        )

    def test_load_already_demodulated(self):
        self.add_signal_to_form("demodulated.wav")
        assert isinstance(self.form, MainController)

        sig_frame = self.form.signal_tab_controller.signal_frames[0]
        sig_frame.ui.cbProtoView.setCurrentText("Hex")
        sig_frame.ui.spinBoxCenterOffset.setValue(0.0459)
        sig_frame.ui.spinBoxCenterOffset.editingFinished.emit()

        self.assertTrue(sig_frame.ui.txtEdProto.toPlainText().startswith("abcd"))

    def test_export_demodulated(self):
        self.add_signal_to_form("esaver.complex16s")
        assert isinstance(self.form, MainController)
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.gvSignal.context_menu_position = QPoint(0, 0)
        cm = self.form.signal_tab_controller.signal_frames[
            0
        ].ui.gvSignal.create_context_menu()
        export_action = next(
            (a for a in cm.actions() if "demodulated" in a.text().lower()), None
        )
        self.assertIsNone(export_action)

        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.cbSignalView.setCurrentIndex(1)
        cm = self.form.signal_tab_controller.signal_frames[
            0
        ].ui.gvSignal.create_context_menu()
        export_action = next(
            (a for a in cm.actions() if "demodulated" in a.text().lower()), None
        )
        self.assertIsNotNone(export_action)
