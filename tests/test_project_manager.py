import os
import random
import unittest

from PyQt5.QtCore import QDir
from PyQt5.QtTest import QTest

import tests.utils_testing
from urh.controller.ProjectDialogController import ProjectDialogController
from urh.controller.MainController import MainController
from urh.signalprocessing.Modulator import Modulator
from tests.utils_testing import get_path_for_data_file
app = tests.utils_testing.app


class TestProjectManager(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.form.project_manager.set_project_folder(get_path_for_data_file(""), ask_for_new_project=False)
        self.cframe = self.form.compare_frame_controller
        self.gframe = self.form.generator_tab_controller

        self.dialog = ProjectDialogController(project_manager=self.form.project_manager, parent=self.form)

    def test_save_modulations(self):
        self.gframe.modulators[0].name = "Test"
        amplitude = random.random()
        self.gframe.modulators[0].carrier_amplitude = amplitude
        self.gframe.modulators[0].carrier_freq_hz = 1337
        self.gframe.modulators[0].carrier_phase_deg = 42
        self.gframe.modulators[0].modulation_type = 1
        self.gframe.modulators[0].sample_rate = 10 ** 3
        self.gframe.modulators.append(Modulator("test 2"))
        self.gframe.modulators = self.gframe.modulators[:2]  # Take only the first two

        self.form.project_manager.saveProject()

        loaded_mods = self.form.project_manager.read_modulators_from_project_file()
        self.assertEqual(len(loaded_mods), 2)

        self.assertEqual(loaded_mods[0].name, "Test")
        self.assertEqual(loaded_mods[1].name, "test 2")
        self.assertEqual(loaded_mods[0].carrier_freq_hz, 1337)
        self.assertEqual(loaded_mods[0].carrier_phase_deg, 42)
        self.assertEqual(loaded_mods[0].modulation_type, 1)
        self.assertEqual(loaded_mods[0].sample_rate, 10 ** 3)

        self.gframe.modulators.clear()
        self.assertEqual(len(self.gframe.modulators), 0)

        self.form.project_manager.set_project_folder(self.form.project_manager.project_path)
        self.assertEqual(len(self.gframe.modulators), 2)

    def test_close_all(self):
        self.form.close_all()
        QTest.qWait(1)
        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        self.form.add_signalfile(get_path_for_data_file("fsk.complex"))
        self.assertEqual(self.form.signal_tab_controller.num_signals, 2)
        self.form.close_all()
        QTest.qWait(1)
        self.assertEqual(self.form.signal_tab_controller.num_signals, 0)
        self.assertEqual(self.form.project_manager.project_file, None)

    def test_project_dialog(self):
        self.dialog.ui.spinBoxFreq.setValue(1e9)
        self.assertEqual(self.dialog.freq, 1e9)

        self.dialog.ui.spinBoxSampleRate.setValue(10e9)
        self.assertEqual(self.dialog.sample_rate, 10e9)

        self.dialog.ui.spinBoxBandwidth.setValue(10)
        self.assertEqual(self.dialog.bandwidth, 10)

        self.dialog.ui.spinBoxGain.setValue(42)
        self.assertEqual(self.dialog.gain, 42)

        self.dialog.ui.txtEdDescription.setPlainText("URH rockz.")
        self.assertEqual(self.dialog.description, "URH rockz.")

        self.dialog.ui.lineEditBroadcastAddress.setText("abcd")
        self.dialog.ui.lineEditBroadcastAddress.textEdited.emit("abcd")
        self.assertEqual(self.dialog.broadcast_address_hex, "abcd")

        if len(self.dialog.participants) == 0:
            self.dialog.ui.btnAddParticipant.click()
            self.assertEqual(len(self.dialog.participants), 1)

        num_participants = len(self.dialog.participants)
        self.dialog.ui.btnAddParticipant.click()
        self.dialog.ui.btnAddParticipant.click()
        self.dialog.ui.btnAddParticipant.click()
        self.assertEqual(len(self.dialog.participants), num_participants + 3)

        self.dialog.ui.btnRemoveParticipant.click()
        self.dialog.ui.btnRemoveParticipant.click()
        self.dialog.ui.btnRemoveParticipant.click()
        self.assertEqual(len(self.dialog.participants), num_participants)

        test_path = os.path.join(QDir.tempPath(), "urh_test")

        self.dialog.ui.lineEdit_Path.setText(test_path)
        self.dialog.ui.lineEdit_Path.textEdited.emit(test_path)
        self.assertEqual(self.dialog.path, test_path)
        self.dialog.ui.btnOK.click()

        self.assertTrue(os.path.isdir(test_path))
