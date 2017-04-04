import os
import random
import string

import numpy
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QCloseEvent
from PyQt5.QtWidgets import QDialog, QCompleter, QDirModel

from urh import constants
from urh.controller.SpectrumDialogController import SpectrumDialogController
from urh.signalprocessing.Participant import Participant
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_project import Ui_ProjectDialog
from urh.util import FileOperator
from urh.util.Errors import Errors
from urh.util.ProjectManager import ProjectManager


class ProjectDialogController(QDialog):
    class ProtocolParticipantModel(QAbstractTableModel):
        participant_rssi_edited = pyqtSignal()

        def __init__(self, participants):
            super().__init__()
            self.participants = participants
            self.header_labels = ["Name", "Shortname", "Color", "Relative RSSI", "Address (hex)"]

        def update(self):
            self.beginResetModel()
            self.endResetModel()

        def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
            return len(self.header_labels)

        def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
            return len(self.participants)

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                return self.header_labels[section]
            return super().headerData(section, orientation, role)

        def data(self, index: QModelIndex, role=Qt.DisplayRole):
            if role == Qt.DisplayRole:
                i = index.row()
                j = index.column()
                part = self.participants[i]
                if j == 0:
                    return part.name
                elif j == 1:
                    return part.shortname
                elif j == 2:
                    return part.color_index
                elif j == 3:
                    return part.relative_rssi
                elif j == 4:
                    return part.address_hex

        def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
            i = index.row()
            j = index.column()
            if i >= len(self.participants):
                return False

            participant = self.participants[i]

            if j == 0:
                participant.name = value
            elif j == 1:
                participant.shortname = value
            elif j == 2:
                participant.color_index = int(value)
            elif j == 3:
                for other in self.participants:
                    if other.relative_rssi == int(value):
                        other.relative_rssi = participant.relative_rssi
                        break
                participant.relative_rssi = int(value)
                self.participant_rssi_edited.emit()
            elif j == 4:
                participant.address_hex = value

            return True

        def flags(self, index: QModelIndex):
            if not index.isValid():
                return Qt.NoItemFlags

            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def __init__(self, new_project=True, project_manager: ProjectManager = None, parent=None):
        super().__init__(parent)
        if not new_project:
            assert project_manager is not None

        self.ui = Ui_ProjectDialog()
        self.ui.setupUi(self)

        if new_project:
            self.participant_table_model = self.ProtocolParticipantModel([])
        else:
            self.participant_table_model = self.ProtocolParticipantModel(project_manager.participants)

            self.ui.spinBoxSampleRate.setValue(project_manager.device_conf["sample_rate"])
            self.ui.spinBoxFreq.setValue(project_manager.device_conf["frequency"])
            self.ui.spinBoxBandwidth.setValue(project_manager.device_conf["bandwidth"])
            self.ui.spinBoxGain.setValue(project_manager.device_conf["gain"])
            self.ui.txtEdDescription.setPlainText(project_manager.description)
            self.ui.lineEdit_Path.setText(project_manager.project_path)
            self.ui.lineEditBroadcastAddress.setText(project_manager.broadcast_address_hex)

            self.ui.btnSelectPath.hide()
            self.ui.lineEdit_Path.setDisabled(True)
            self.setWindowTitle("Edit project settings")
            self.ui.lNewProject.setText("Edit project")
            self.ui.btnOK.setText("Accept")

        self.ui.tblParticipants.setModel(self.participant_table_model)
        self.ui.tblParticipants.setItemDelegateForColumn(2, ComboBoxDelegate([""] * len(constants.PARTICIPANT_COLORS),
                                                                             colors=constants.PARTICIPANT_COLORS,
                                                                             parent=self))

        self.__set_relative_rssi_delegate()
        "(([a-fA-F]|[0-9]){2}){3}"
        self.ui.lineEditBroadcastAddress.setValidator(QRegExpValidator(QRegExp("([a-fA-F ]|[0-9]){,}")))

        self.sample_rate = self.ui.spinBoxSampleRate.value()
        self.freq = self.ui.spinBoxFreq.value()
        self.bandwidth = self.ui.spinBoxBandwidth.value()
        self.gain = self.ui.spinBoxGain.value()
        self.description = self.ui.txtEdDescription.toPlainText()
        self.broadcast_address_hex = self.ui.lineEditBroadcastAddress.text()

        self.ui.btnRemoveParticipant.setDisabled(len(self.participants) <= 1)

        self.path = self.ui.lineEdit_Path.text()
        self.new_project = new_project
        self.committed = False
        self.setModal(True)

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEdit_Path.setCompleter(completer)

        self.create_connects()

        if new_project:
            self.ui.lineEdit_Path.setText(os.path.realpath(os.path.join(os.curdir, "new")))

        self.on_line_edit_path_text_edited()

        self.open_editors()

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass


    def __set_relative_rssi_delegate(self):
        n = len(self.participants)
        if n == 0:
            items = []
        elif n == 1:
            items = ["0"]
        else:
            items = [str(i) for i in range(n)]
            items[0] += " (low)"
            items[-1] += " (high)"

        for row in range(len(self.participants)):
            self.ui.tblParticipants.closePersistentEditor(self.participant_table_model.index(row, 3))

        self.ui.tblParticipants.setItemDelegateForColumn(3, ComboBoxDelegate(items, parent=self))

    def __on_relative_rssi_edited(self):
        self.__set_relative_rssi_delegate()
        self.open_editors()

    @property
    def participants(self):
        """

        :rtype: list of Participant
        """
        return self.participant_table_model.participants

    def create_connects(self):
        self.ui.spinBoxFreq.valueChanged.connect(self.on_spin_box_frequency_value_changed)
        self.ui.spinBoxSampleRate.valueChanged.connect(self.on_spin_box_sample_rate_value_changed)
        self.ui.spinBoxBandwidth.valueChanged.connect(self.on_spin_box_bandwidth_value_changed)
        self.ui.spinBoxGain.valueChanged.connect(self.on_spin_box_gain_value_changed)
        self.ui.txtEdDescription.textChanged.connect(self.on_txt_edit_description_text_changed)
        self.ui.lineEditBroadcastAddress.textEdited.connect(self.on_line_edit_broadcast_address_text_edited)

        self.ui.btnAddParticipant.clicked.connect(self.on_btn_add_participant_clicked)
        self.ui.btnRemoveParticipant.clicked.connect(self.on_btn_remove_participant_clicked)

        self.ui.lineEdit_Path.textEdited.connect(self.on_line_edit_path_text_edited)
        self.ui.btnOK.clicked.connect(self.on_button_ok_clicked)
        self.ui.btnSelectPath.clicked.connect(self.on_btn_select_path_clicked)
        self.ui.lOpenSpectrumAnalyzer.linkActivated.connect(self.on_spectrum_analyzer_link_activated)

        self.participant_table_model.participant_rssi_edited.connect(self.__on_relative_rssi_edited)

    def set_path(self, path):
        self.path = path
        self.ui.lineEdit_Path.setText(self.path)
        name = os.path.basename(os.path.normpath(self.path))
        self.ui.lblName.setText(name)

        self.ui.lblNewPath.setVisible(not os.path.isdir(self.path))

    def open_editors(self):
        for row in range(len(self.participants)):
            self.ui.tblParticipants.openPersistentEditor(self.participant_table_model.index(row, 2))
            self.ui.tblParticipants.openPersistentEditor(self.participant_table_model.index(row, 3))

    def closeEvent(self, event: QCloseEvent):
        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    @pyqtSlot(float)
    def on_spin_box_sample_rate_value_changed(self, value: float):
        self.sample_rate = value

    @pyqtSlot(float)
    def on_spin_box_frequency_value_changed(self, value: float):
        self.freq = value

    @pyqtSlot(float)
    def on_spin_box_bandwidth_value_changed(self, value: float):
        self.bandwidth = value

    @pyqtSlot(int)
    def on_spin_box_gain_value_changed(self, value: int):
        self.gain = value

    @pyqtSlot()
    def on_line_edit_path_text_edited(self):
        self.set_path(self.ui.lineEdit_Path.text())

    @pyqtSlot()
    def on_txt_edit_description_text_changed(self):
        self.description = self.ui.txtEdDescription.toPlainText()

    @pyqtSlot()
    def on_button_ok_clicked(self):
        self.path = os.path.realpath(self.path)
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except Exception:
                pass

        # Path should be created now, if not raise Error
        if not os.path.exists(self.path):
            Errors.invalid_path(self.path)
            return

        self.committed = True
        self.close()

    @pyqtSlot(str)
    def on_line_edit_broadcast_address_text_edited(self, value: str):
        self.broadcast_address_hex = value

    @pyqtSlot()
    def on_btn_select_path_clicked(self):
        directory = FileOperator.get_directory()
        if directory:
            self.set_path(directory)

    @pyqtSlot(str, dict)
    def set_recording_params_from_spectrum_analyzer_link(self, dev_name, args: dict):
        self.ui.spinBoxFreq.setValue(args["frequency"])
        self.ui.spinBoxSampleRate.setValue(args["sample_rate"])
        self.ui.spinBoxBandwidth.setValue(args["bandwidth"])
        self.ui.spinBoxGain.setValue(args["gain"])

    @pyqtSlot(str)
    def on_spectrum_analyzer_link_activated(self, link: str):
        if link == "open_spectrum_analyzer":
            r = SpectrumDialogController(ProjectManager(None), parent=self)
            if r.has_empty_device_list:
                Errors.no_device()
                r.close()
                return

            r.recording_parameters.connect(self.set_recording_params_from_spectrum_analyzer_link)
            r.show()

    @pyqtSlot()
    def on_btn_add_participant_clicked(self):
        used_shortnames = {p.shortname for p in self.participants}
        used_colors = set(p.color_index for p in self.participants)
        avail_colors = set(range(0, len(constants.PARTICIPANT_COLORS))) - used_colors
        if len(avail_colors) > 0:
            color_index = avail_colors.pop()
        else:
            color_index = random.choice(range(len(constants.PARTICIPANT_COLORS)))

        num_chars = 0
        participant = None
        while participant is None:
            num_chars += 1
            for c in string.ascii_uppercase:
                shortname = num_chars * str(c)
                if shortname not in used_shortnames:
                    participant = Participant("Device " + shortname, shortname=shortname, color_index=color_index)
                    break

        self.participants.append(participant)
        participant.relative_rssi = len(self.participants) - 1
        self.__set_relative_rssi_delegate()
        self.participant_table_model.update()
        self.ui.btnRemoveParticipant.setEnabled(True)
        self.open_editors()

    @pyqtSlot()
    def on_btn_remove_participant_clicked(self):
        if len(self.participants) <= 1:
            return

        selected = self.ui.tblParticipants.selectionModel().selection()
        if selected.isEmpty():
            start, end = len(self.participants) - 1, len(self.participants) - 1  # delete last element
        else:
            start, end = numpy.min([rng.top() for rng in selected]), numpy.max([rng.bottom() for rng in selected])

        if end - start >= len(self.participants) - 1:
            # Ensure one left
            start += 1

        del self.participants[start:end + 1]
        num_removed = (end + 1) - start
        for participant in self.participants:
            if participant.relative_rssi > len(self.participants) - 1:
                participant.relative_rssi -= num_removed
        self.__set_relative_rssi_delegate()
        self.participant_table_model.update()
        self.ui.btnRemoveParticipant.setDisabled(len(self.participants) <= 1)
        self.open_editors()
