import os
import tempfile

from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase


class TestMaincontrollerGUI(QtTestCase):
    def test_open_recent_file(self):
        # Ensure we have at least one recent action
        self.add_signal_to_form("esaver.complex")
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

        self.form.recentFileActionList[0].trigger()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 2)

    def test_open_rect_directory(self):
        test_dir = os.path.join(tempfile.gettempdir(), "project_test")
        try:
            os.mkdir(test_dir)
        except OSError:
            pass

        self.form.project_manager.set_project_folder(test_dir, ask_for_new_project=False)

        self.assertIn("project_test", self.form.recentFileActionList[0].text())

    def test_update_decodings(self):
        self.form.update_decodings()
        self.assertTrue(True)

    def test_options_changed(self):
        self.add_signal_to_form("esaver.complex")
        self.form.on_options_changed({"rel_symbol_length": 0, "show_pause_as_time": True, "default_view": 2})
        QApplication.instance().processEvents()
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.currentIndex(), 2)
