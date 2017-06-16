import os
import tempfile

from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from urh.controller.OptionsController import OptionsController


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
        self.form.on_options_changed({"show_pause_as_time": True, "default_view": 2})
        QApplication.instance().processEvents()
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.currentIndex(), 2)

    def test_open_plain_bits(self):
        bits = ["1010111000110001010101010101",
                "1010111110010010101",
                "1111010100101010101010101010"]

        filename = os.path.join(tempfile.gettempdir(), "test_plain_bits.txt")
        with open(filename, "w") as f:
            f.write(os.linesep.join(bits))

        self.form.compare_frame_controller.ui.cbProtoView.setCurrentIndex(0)
        self.wait_before_new_file()
        self.form.add_files([filename])

        for i, bit_seq in enumerate(bits):
            table_data = "".join(map(str, self.form.compare_frame_controller.protocol_model.display_data[i]))
            self.assertEqual(bit_seq, table_data)

    def test_open_options_dialog(self):
        self.form.show_options_dialog_specific_tab(1)
        w = next((w for w in QApplication.topLevelWidgets() if isinstance(w, OptionsController)), None) # type: OptionsController
        self.assertIsNotNone(w)
        self.assertEqual(w.ui.tabWidget.currentIndex(), 1)
        w.close()
