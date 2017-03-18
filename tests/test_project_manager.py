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
from urh.util.Logger import logger

app = tests.utils_testing.get_app()


class TestProjectManager(unittest.TestCase):
    def setUp(self):
        logger.debug("Init form")
        self.form = MainController()
        logger.debug("Initialized form")
        app.processEvents()
        QTest.qWait(25)
        self.form.project_manager.set_project_folder(get_path_for_data_file(""), ask_for_new_project=False)
        self.cframe = self.form.compare_frame_controller
        self.gframe = self.form.generator_tab_controller

        self.dialog = ProjectDialogController(project_manager=self.form.project_manager, parent=self.form)

    def tearDown(self):
        self.dialog.close()
        self.dialog.setParent(None)
        self.dialog.deleteLater()
        app.processEvents()
        QTest.qWait(10)
        self.form.close()
        self.form.deleteLater()
        app.processEvents()
        QTest.qWait(10)

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
        app.processEvents()
        QTest.qWait(10)
        self.assertEqual(self.form.signal_tab_controller.num_signals, 0)
        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        self.form.add_signalfile(get_path_for_data_file("fsk.complex"))
        self.assertEqual(self.form.signal_tab_controller.num_signals, 2)
        self.form.close_all()
        app.processEvents()
        QTest.qWait(10)
        self.assertEqual(self.form.signal_tab_controller.num_signals, 0)
        self.assertEqual(self.form.project_manager.project_file, None)

    def test_project_dialog(self):
        frequency = 1e9
        sample_rate = 10e9
        bandwidth = 10
        gain = 42
        descr = "URH rockz."

        self.dialog.ui.spinBoxFreq.setValue(frequency)
        self.assertEqual(self.dialog.freq, frequency)

        self.dialog.ui.spinBoxSampleRate.setValue(sample_rate)
        self.assertEqual(self.dialog.sample_rate, sample_rate)

        self.dialog.ui.spinBoxBandwidth.setValue(bandwidth)
        self.assertEqual(self.dialog.bandwidth, bandwidth)

        self.dialog.ui.spinBoxGain.setValue(gain)
        self.assertEqual(self.dialog.gain, gain)

        self.dialog.ui.txtEdDescription.setPlainText(descr)
        self.assertEqual(self.dialog.description, descr)

        self.dialog.ui.lineEditBroadcastAddress.setText("abcd")
        self.dialog.ui.lineEditBroadcastAddress.textEdited.emit("abcd")
        self.assertEqual(self.dialog.broadcast_address_hex, "abcd")

        if len(self.dialog.participants) == 0:
            self.dialog.ui.btnAddParticipant.click()
            self.assertEqual(len(self.dialog.participants), 1)

        model = self.dialog.participant_table_model
        model.setData(model.index(0, 0), "Testing")
        model.setData(model.index(0, 1), "T")
        model.setData(model.index(0, 2), 5)
        model.setData(model.index(0, 3), 0)
        model.setData(model.index(0, 4), "aaaa")
        participant = self.dialog.participants[0]
        self.assertEqual(participant.name, "Testing")
        self.assertEqual(participant.shortname, "T")
        self.assertEqual(participant.color_index, 5)
        self.assertEqual(participant.relative_rssi, 0)
        self.assertEqual(participant.address_hex, "aaaa")

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

        self.form.project_manager.from_dialog(self.dialog)

        self.dialog = ProjectDialogController(project_manager=self.form.project_manager, parent=self.form, new_project=False)
        self.assertEqual(self.dialog.ui.spinBoxFreq.value(), frequency)
        self.assertEqual(self.dialog.ui.spinBoxSampleRate.value(), sample_rate)
        self.assertEqual(self.dialog.ui.spinBoxBandwidth.value(), bandwidth)
        self.assertEqual(self.dialog.ui.spinBoxGain.value(), gain)
        self.assertEqual(self.dialog.ui.txtEdDescription.toPlainText(), descr)
        self.assertFalse(self.dialog.ui.lineEdit_Path.isEnabled())
