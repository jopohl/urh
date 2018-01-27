import os

from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QRegExpValidator, QCloseEvent
from PyQt5.QtWidgets import QDialog, QCompleter, QDirModel

from urh import constants
from urh.controller.dialogs.SpectrumDialogController import SpectrumDialogController
from urh.dev import config
from urh.models.ParticipantTableModel import ParticipantTableModel
from urh.signalprocessing.Participant import Participant
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_project import Ui_ProjectDialog
from urh.util import FileOperator
from urh.util.Errors import Errors
from urh.util.ProjectManager import ProjectManager


class ProjectDialog(QDialog):
    def __init__(self, new_project=True, project_manager: ProjectManager = None, parent=None):
        super().__init__(parent)
        if not new_project:
            assert project_manager is not None

        self.ui = Ui_ProjectDialog()
        self.ui.setupUi(self)

        if new_project:
            self.participant_table_model = ParticipantTableModel([])
        else:
            self.participant_table_model = ParticipantTableModel(project_manager.participants)

            self.ui.spinBoxSampleRate.setValue(project_manager.device_conf["sample_rate"])
            self.ui.spinBoxFreq.setValue(project_manager.device_conf["frequency"])
            self.ui.spinBoxBandwidth.setValue(project_manager.device_conf["bandwidth"])
            self.ui.spinBoxGain.setValue(project_manager.device_conf.get("gain", config.DEFAULT_GAIN))
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
        # add two participants
        if self.participant_table_model.rowCount() == 0:
            self.ui.btnAddParticipant.click()
            self.ui.btnAddParticipant.click()

        if new_project:
            self.ui.lineEdit_Path.setText(os.path.realpath(os.path.join(os.curdir, "new")))

        self.on_line_edit_path_text_edited()

        self.refresh_participant_table()

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

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

        self.participant_table_model.participant_added.connect(self.on_participant_added)
        self.participant_table_model.participants_removed.connect(self.on_participants_removed)
        self.participant_table_model.participant_edited.connect(self.on_participant_edited)

    def set_path(self, path):
        self.path = path
        self.ui.lineEdit_Path.setText(self.path)
        name = os.path.basename(os.path.normpath(self.path))
        self.ui.lblName.setText(name)

        self.ui.lblNewPath.setVisible(not os.path.isdir(self.path))

    def refresh_participant_table(self):
        n = len(self.participants)
        items = [str(i) for i in range(n)]
        if len(items) >= 2:
            items[0] += " (low)"
            items[-1] += " (high)"

        for row in range(n):
            self.ui.tblParticipants.closePersistentEditor(self.participant_table_model.index(row, 3))

        self.ui.tblParticipants.setItemDelegateForColumn(3, ComboBoxDelegate(items, parent=self))
        self.ui.btnRemoveParticipant.setEnabled(len(self.participants) > 1)

        for row in range(n):
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
        self.ui.spinBoxGain.setValue(args.get("gain", config.DEFAULT_GAIN))

    @pyqtSlot(str)
    def on_spectrum_analyzer_link_activated(self, link: str):
        if link == "open_spectrum_analyzer":
            r = SpectrumDialogController(ProjectManager(None), parent=self)
            if r.has_empty_device_list:
                Errors.no_device()
                r.close()
                return

            r.device_parameters_changed.connect(self.set_recording_params_from_spectrum_analyzer_link)
            r.show()

    @pyqtSlot()
    def on_btn_add_participant_clicked(self):
        self.participant_table_model.add_participant()

    @pyqtSlot()
    def on_btn_remove_participant_clicked(self):
        self.participant_table_model.remove_participants(self.ui.tblParticipants.selectionModel().selection())

    @pyqtSlot()
    def on_participant_added(self):
        self.refresh_participant_table()

    @pyqtSlot()
    def on_participants_removed(self):
        self.refresh_participant_table()

    @pyqtSlot()
    def on_participant_edited(self):
        self.participant_table_model.update()
        self.refresh_participant_table()
