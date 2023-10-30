import os
import sys
import tempfile
import wave

import numpy as np
from PyQt5.QtCore import QTimer, QDir
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import settings
from urh.controller.MainController import MainController
from urh.controller.dialogs.CSVImportDialog import CSVImportDialog
from urh.controller.dialogs.OptionsDialog import OptionsDialog


class TestMaincontrollerGUI(QtTestCase):
    def test_open_recent_file(self):
        settings.write("recentFiles", [])

        # Ensure we have at least one recent action
        self.form.add_files([get_path_for_data_file("esaver.complex16s")])
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

        self.form.recentFileActionList[0].trigger()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 2)

    def test_open_rect_directory(self):
        test_dir = os.path.join(tempfile.gettempdir(), "project_test")
        try:
            os.mkdir(test_dir)
        except OSError:
            pass

        self.form.project_manager.set_project_folder(
            test_dir, ask_for_new_project=False
        )

        self.assertIn("project_test", self.form.recentFileActionList[0].text())

    def test_update_decodings(self):
        self.form.update_decodings()
        self.assertTrue(True)

    def test_options_changed(self):
        self.add_signal_to_form("esaver.complex16s")
        self.form.on_options_changed({"show_pause_as_time": True, "default_view": 2})
        QApplication.instance().processEvents()
        self.assertEqual(
            self.form.signal_tab_controller.signal_frames[
                0
            ].ui.cbProtoView.currentIndex(),
            2,
        )

    def test_open_plain_bits(self):
        bits = [
            "1010111000110001010101010101",
            "1010111110010010101",
            "1111010100101010101010101010",
        ]

        filename = os.path.join(tempfile.gettempdir(), "test_plain_bits.txt")
        with open(filename, "w") as f:
            f.write(os.linesep.join(bits))

        self.form.compare_frame_controller.ui.cbProtoView.setCurrentIndex(0)
        self.form.add_files([filename])

        for i, bit_seq in enumerate(bits):
            table_data = "".join(
                map(
                    str,
                    self.form.compare_frame_controller.protocol_model.display_data[i],
                )
            )
            self.assertEqual(bit_seq, table_data)

    def test_open_options_dialog(self):
        self.form.show_options_dialog_specific_tab(1)
        w = next(
            (w for w in QApplication.topLevelWidgets() if isinstance(w, OptionsDialog)),
            None,
        )  # type: OptionsDialog
        self.assertIsNotNone(w)
        self.assertEqual(w.ui.tabWidget.currentIndex(), 1)
        w.close()

    def test_import_csv(self):
        if sys.platform == "darwin":
            return

        def accept_csv_dialog():
            for w in QApplication.topLevelWidgets():
                if isinstance(w, CSVImportDialog):
                    w.accept()
            timer.stop()

        timer = QTimer(self.form)
        timer.setInterval(50)
        timer.timeout.connect(accept_csv_dialog)

        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)
        timer.start()
        self.form.add_files([self.get_path_for_filename("csvtest.csv")])

        self.assertFalse(timer.isActive())

        self.assertEqual(
            self.form.signal_tab_controller.signal_frames[0].signal.num_samples, 100
        )
        self.assertTrue(os.path.isfile(self.get_path_for_filename("csvtest.complex")))
        timer.start()
        self.form.add_files([self.get_path_for_filename("csvtest.csv")])

        self.assertEqual(self.form.signal_tab_controller.num_frames, 2)
        self.assertTrue(os.path.isfile(self.get_path_for_filename("csvtest_1.complex")))

        os.remove(self.get_path_for_filename("csvtest.complex"))
        os.remove(self.get_path_for_filename("csvtest_1.complex"))

    def test_load_single_channel_wav(self):
        filename = os.path.join(tempfile.gettempdir(), "test_single_channel.wav")
        f = wave.open(filename, "w")
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(2e6)
        f.writeframes(np.array([1, 2, 3, 4], dtype=np.uint8))
        f.close()

        self.add_signal_to_form(filename)
        sig_frame = self.form.signal_tab_controller.signal_frames[0]
        self.assertEqual(sig_frame.signal.sample_rate, 2e6)
        self.assertEqual(sig_frame.signal.num_samples, 4)
        self.assertNotEqual(sig_frame.signal.iq_array.real.sum(), 0)
        self.assertEqual(sig_frame.signal.iq_array.imag.sum(), 0)

    def test_load_stereo_wav(self):
        filename = os.path.join(tempfile.gettempdir(), "test_stereo.wav")
        f = wave.open(filename, "w")
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(10e6)
        f.writeframes(np.array([23556, 2132, 111, 11111, 3455, 2324], dtype=np.int16))
        f.close()

        self.add_signal_to_form(filename)
        sig_frame = self.form.signal_tab_controller.signal_frames[0]
        self.assertEqual(sig_frame.signal.sample_rate, 10e6)
        self.assertEqual(sig_frame.signal.num_samples, 3)
        self.assertNotEqual(sig_frame.signal.iq_array.real.sum(), 0)
        self.assertNotEqual(sig_frame.signal.iq_array.imag.sum(), 0)

    def test_remove_file_from_directory_tree_view(self):
        assert isinstance(self.form, MainController)
        file_proxy_model = self.form.file_proxy_model
        file_model = self.form.filemodel
        self.form.ui.fileTree.setRootIndex(
            file_proxy_model.mapFromSource(file_model.index(QDir.tempPath()))
        )

        menu = self.form.ui.fileTree.create_context_menu()
        remove_action = next(
            (action for action in menu.actions() if action.text() == "Delete"), None
        )
        self.assertIsNotNone(remove_action)

        f = os.path.join(QDir.tempPath(), "test")
        open(f, "w").close()
        self.assertTrue(os.path.isfile(f))
        self.form.ui.fileTree.setCurrentIndex(
            file_proxy_model.mapFromSource(file_model.index(f))
        )

        remove_action.trigger()
        self.assertFalse(os.path.isfile(f))
