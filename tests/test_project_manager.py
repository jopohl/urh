import os
import random
import tempfile

from PyQt5.QtCore import QDir, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.dialogs.ProjectDialog import ProjectDialog
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant


class TestProjectManager(QtTestCase):
    def setUp(self):
        super().setUp()
        if os.path.isfile(get_path_for_data_file("URHProject.xml")):
            os.remove(get_path_for_data_file("URHProject.xml"))
        self.form.project_manager.set_project_folder(get_path_for_data_file(""), ask_for_new_project=False)
        self.gframe = self.form.generator_tab_controller

    def test_load_protocol_file(self):
        self.wait_before_new_file()
        self.form.add_protocol_file(self.get_path_for_filename("protocol_wsp.proto.xml"))
        self.assertEqual(len(self.form.compare_frame_controller.proto_analyzer.messages), 6)

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

        self.form.save_project()

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

        self.form.project_manager.project_file = None  # prevent saving of the zero modulators
        self.form.project_manager.set_project_folder(self.form.project_manager.project_path, close_all=False)
        self.assertEqual(len(self.gframe.modulators), 2)

    def test_close_all(self):
        self.form.close_all()
        QApplication.instance().processEvents()
        QTest.qWait(self.CLOSE_TIMEOUT)
        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)
        self.add_signal_to_form("ask.complex")
        self.add_signal_to_form("fsk.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 2)
        self.form.close_all()
        QApplication.instance().processEvents()
        QTest.qWait(self.CLOSE_TIMEOUT)
        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)
        self.assertEqual(self.form.project_manager.project_file, None)

    def test_save_and_load_participants(self):
        target_dir = os.path.join(tempfile.gettempdir(), "urh", "multi_participant_test")
        os.makedirs(target_dir, exist_ok=True)
        if os.path.isfile(os.path.join(target_dir, constants.PROJECT_FILE)):
            os.remove(os.path.join(target_dir, constants.PROJECT_FILE))
        self.form.project_manager.set_project_folder(target_dir, ask_for_new_project=False)
        self.form.project_manager.participants = [Participant("Alice", "A"), Participant("Bob", "B")]

        self.add_signal_to_form("esaver.complex")
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames[0].proto_analyzer.messages), 3)
        self.add_signal_to_form("two_participants.complex")
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames[1].proto_analyzer.messages), 18)
        self.add_signal_to_form("fsk.complex")
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames[2].proto_analyzer.messages), 1)

        self.assertEqual(self.form.compare_frame_controller.protocol_model.row_count, 22)

        target = {0: "A", 1: "A", 2: "B", 3: "B", 4: "A", 5: "B", 6: "A", 7: "A", 8: "A", 9: "B", 10: "B",
                  11: "A", 12: "B", 13: "A", 14: "A", 15: "B", 16: "A", 17: "B", 18: "B", 19: "B", 20: "A", 21: "B"}

        for row, shortname in target.items():
            participant = next(p for p in self.form.project_manager.participants if p.shortname == shortname)
            self.form.compare_frame_controller.proto_analyzer.messages[row].participant = participant

        self.form.compare_frame_controller.proto_tree_model.rootItem.child(0).child(0).show = False
        self.assertEqual(self.form.compare_frame_controller.protocol_model.row_count, 19)

        for row, shortname in target.items():
            row -= 3
            if row >= 0:
                self.assertEqual(self.form.compare_frame_controller.proto_analyzer.messages[row].participant.shortname,
                                 shortname)

        self.form.compare_frame_controller.refresh_assigned_participants_ui()

        self.form.save_project()
        self.form.close_all()
        self.wait_before_new_file()
        self.assertEqual(self.form.compare_frame_controller.protocol_model.row_count, 0)
        self.form.project_manager.set_project_folder(target_dir, ask_for_new_project=False)

        self.assertEqual(self.form.compare_frame_controller.protocol_model.row_count, 22)
        for row, shortname in target.items():
            self.assertEqual(self.form.compare_frame_controller.proto_analyzer.messages[row].participant.shortname,
                             shortname, msg=str(row))

    def test_save_and_load_with_fieldtypes(self):
        target_dir = os.path.join(tempfile.gettempdir(), "urh", "project_fieldtype_test")
        os.makedirs(target_dir, exist_ok=True)
        if os.path.isfile(os.path.join(target_dir, constants.PROJECT_FILE)):
            os.remove(os.path.join(target_dir, constants.PROJECT_FILE))
        self.form.project_manager.set_project_folder(target_dir, ask_for_new_project=False)

        self.add_signal_to_form("esaver.complex")
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames[0].proto_analyzer.messages), 3)

        preamble_field_type = next(ft for ft in self.form.compare_frame_controller.field_types
                                   if ft.function == FieldType.Function.PREAMBLE)  # type: FieldType

        sync_field_type = next(ft for ft in self.form.compare_frame_controller.field_types
                               if ft.function == FieldType.Function.SYNC)  # type: FieldType

        checksum_field_type = next(ft for ft in self.form.compare_frame_controller.field_types
                                   if ft.function == FieldType.Function.CHECKSUM)  # type: FieldType

        self.form.compare_frame_controller.ui.cbProtoView.setCurrentText("Hex")
        self.form.compare_frame_controller.add_protocol_label(0, 9, 0, 1, False)
        self.__set_label_name(0, preamble_field_type.caption)

        self.form.compare_frame_controller.add_protocol_label(10, 13, 0, 1, False)
        self.__set_label_name(1, sync_field_type.caption)

        self.form.compare_frame_controller.add_protocol_label(14, 16, 0, 1, False)
        self.__set_label_name(2, checksum_field_type.caption)

        self.assertEqual(self.form.compare_frame_controller.active_message_type[0].field_type, preamble_field_type)
        self.assertEqual(self.form.compare_frame_controller.active_message_type[1].field_type, sync_field_type)
        self.assertEqual(self.form.compare_frame_controller.active_message_type[2].field_type, checksum_field_type)

        self.form.close_all()
        self.wait_before_new_file()
        self.assertEqual(len(self.form.compare_frame_controller.active_message_type), 0)
        self.form.project_manager.set_project_folder(target_dir, ask_for_new_project=False)

        self.assertEqual(len(self.form.compare_frame_controller.active_message_type), 3)

        preamble_field_type = next(ft for ft in self.form.compare_frame_controller.field_types
                                   if ft.function == FieldType.Function.PREAMBLE)  # type: FieldType

        sync_field_type = next(ft for ft in self.form.compare_frame_controller.field_types
                               if ft.function == FieldType.Function.SYNC)  # type: FieldType

        checksum_field_type = next(ft for ft in self.form.compare_frame_controller.field_types
                                   if ft.function == FieldType.Function.CHECKSUM)  # type: FieldType

        self.assertEqual(self.form.compare_frame_controller.active_message_type[0].field_type, preamble_field_type)
        self.assertEqual(self.form.compare_frame_controller.active_message_type[1].field_type, sync_field_type)
        self.assertEqual(self.form.compare_frame_controller.active_message_type[2].field_type, checksum_field_type)

    def __set_label_name(self, index: int, name: str):
        list_model = self.form.compare_frame_controller.ui.listViewLabelNames.model()
        list_model.setData(list_model.createIndex(index, 0), name, role=Qt.EditRole)

    def test_project_dialog(self):
        frequency = 1e9
        sample_rate = 10e9
        bandwidth = 10
        gain = 42
        descr = "URH rockz."

        dialog = ProjectDialog(project_manager=self.form.project_manager, parent=self.form)

        dialog.ui.spinBoxFreq.setValue(frequency)
        self.assertEqual(dialog.freq, frequency)

        dialog.ui.spinBoxSampleRate.setValue(sample_rate)
        self.assertEqual(dialog.sample_rate, sample_rate)

        dialog.ui.spinBoxBandwidth.setValue(bandwidth)
        self.assertEqual(dialog.bandwidth, bandwidth)

        dialog.ui.spinBoxGain.setValue(gain)
        self.assertEqual(dialog.gain, gain)

        dialog.ui.txtEdDescription.setPlainText(descr)
        self.assertEqual(dialog.description, descr)

        dialog.ui.lineEditBroadcastAddress.setText("abcd")
        dialog.ui.lineEditBroadcastAddress.textEdited.emit("abcd")
        self.assertEqual(dialog.broadcast_address_hex, "abcd")

        if len(dialog.participants) == 0:
            dialog.ui.btnAddParticipant.click()
            self.assertEqual(len(dialog.participants), 1)

        model = dialog.participant_table_model
        model.setData(model.index(0, 0), "Testing")
        model.setData(model.index(0, 1), "T")
        model.setData(model.index(0, 2), 5)
        model.setData(model.index(0, 3), 0)
        model.setData(model.index(0, 4), "aaaa")
        participant = dialog.participants[0]
        self.assertEqual(participant.name, "Testing")
        self.assertEqual(participant.shortname, "T")
        self.assertEqual(participant.color_index, 5)
        self.assertEqual(participant.relative_rssi, 0)
        self.assertEqual(participant.address_hex, "aaaa")

        num_participants = len(dialog.participants)
        dialog.ui.btnAddParticipant.click()
        dialog.ui.btnAddParticipant.click()
        dialog.ui.btnAddParticipant.click()
        self.assertEqual(len(dialog.participants), num_participants + 3)

        dialog.ui.btnRemoveParticipant.click()
        dialog.ui.btnRemoveParticipant.click()
        dialog.ui.btnRemoveParticipant.click()
        self.assertEqual(len(dialog.participants), num_participants)

        test_path = os.path.join(QDir.tempPath(), "urh_test")

        dialog.ui.lineEdit_Path.setText(test_path)
        dialog.ui.lineEdit_Path.textEdited.emit(test_path)
        self.assertEqual(dialog.path, test_path)
        dialog.ui.btnOK.click()

        self.form.ui.tabWidget.setCurrentWidget(self.form.ui.tab_protocol)
        self.form.compare_frame_controller.ui.tabWidget.setCurrentWidget(
            self.form.compare_frame_controller.ui.tab_participants)
        self.assertGreater(self.form.compare_frame_controller.participant_list_model.rowCount(), 0)

        self.assertTrue(os.path.isdir(test_path))

        self.form.project_manager.from_dialog(dialog)

        dialog = ProjectDialog(project_manager=self.form.project_manager, parent=self.form, new_project=False)
        self.assertEqual(dialog.ui.spinBoxFreq.value(), frequency)
        self.assertEqual(dialog.ui.spinBoxSampleRate.value(), sample_rate)
        self.assertEqual(dialog.ui.spinBoxBandwidth.value(), bandwidth)
        self.assertEqual(dialog.ui.spinBoxGain.value(), gain)
        self.assertEqual(dialog.ui.txtEdDescription.toPlainText(), descr)
        self.assertFalse(dialog.ui.lineEdit_Path.isEnabled())
