import os

from PyQt5.QtCore import pyqtSlot, QCoreApplication
from PyQt5.QtWidgets import QDialog, QCompleter, QDirModel, QTableWidgetItem

from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import Mode
from urh.signalprocessing.Participant import Participant
from urh.ui.ui_project import Ui_ProjectDialog
from urh.util import FileOperator
from urh.util.Errors import Errors

import string

class ProjectDialogController(QDialog):
    def __init__(self, new_project=True, parent=None):
        super().__init__(parent)

        self.ui = Ui_ProjectDialog()
        self.ui.setupUi(self)

        self.sample_rate = self.ui.spinBoxSampleRate.value()
        self.freq = self.ui.spinBoxFreq.value()
        self.bandwidth = self.ui.spinBoxBandwidth.value()
        self.gain = self.ui.spinBoxGain.value()
        self.description = self.ui.txtEdDescription.toPlainText()

        self.participants = self.__read_participants_from_table()
        self.ui.btnRemoveParticipant.setDisabled(self.ui.tblParticipants.rowCount() <= 1)

        self.path = self.ui.lineEdit_Path.text()
        self.new_project = new_project
        self.commited = False
        self.setModal(True)

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEdit_Path.setCompleter(completer)

        if not self.new_project:
            self.ui.btnSelectPath.hide()
            self.ui.lineEdit_Path.setDisabled(True)

        self.ui.lblNewPath.hide()
        self.create_connects()

        self.ui.lineEdit_Path.setText(os.path.realpath(os.path.join(os.curdir, "new")))
        self.on_path_edited()

    def create_connects(self):
        self.ui.spinBoxFreq.valueChanged.connect(self.on_frequency_changed)
        self.ui.spinBoxSampleRate.valueChanged.connect(self.on_sample_rate_changed)
        self.ui.spinBoxBandwidth.valueChanged.connect(self.on_bandwidth_changed)
        self.ui.spinBoxGain.valueChanged.connect(self.on_gain_changed)
        self.ui.txtEdDescription.textChanged.connect(self.on_description_changed)

        self.ui.btnAddParticipant.clicked.connect(self.on_btn_add_participant_clicked)
        self.ui.btnRemoveParticipant.clicked.connect(self.on_btn_remove_participant_clicked)
        self.ui.tblParticipants.itemChanged.connect(self.on_participant_item_changed)

        self.ui.lineEdit_Path.textEdited.connect(self.on_path_edited)
        self.ui.btnOK.clicked.connect(self.on_button_ok_clicked)
        self.ui.btnSelectPath.clicked.connect(self.on_btn_select_path_clicked)
        self.ui.lOpenSpectrumAnalyzer.linkActivated.connect(self.on_spectrum_analyzer_link_activated)

    def __read_participants_from_table(self):
        """

        :rtype: list of Participant
        """
        result = []
        for i in range(self.ui.tblParticipants.rowCount()):
            name = self.ui.tblParticipants.item(i, 0).text()
            shortname = self.ui.tblParticipants.item(i, 1).text()
            address_hex = self.ui.tblParticipants.item(i, 2).text()
            result.append(Participant(name, shortname, address_hex))
        return result

    def __write_participants_to_table(self):
        self.ui.tblParticipants.blockSignals(True)
        self.ui.tblParticipants.setRowCount(0)
        for i, prtcpnt in enumerate(self.participants):
            self.ui.tblParticipants.insertRow(i)
            self.ui.tblParticipants.setItem(i, 0, QTableWidgetItem(prtcpnt.name, 0))
            self.ui.tblParticipants.setItem(i, 1, QTableWidgetItem(prtcpnt.shortname, 0))
            self.ui.tblParticipants.setItem(i, 2, QTableWidgetItem(prtcpnt.address_hex, 0))
        self.ui.tblParticipants.blockSignals(False)

    def on_sample_rate_changed(self):
        self.sample_rate = self.ui.spinBoxSampleRate.value()

    def on_frequency_changed(self):
        self.freq = self.ui.spinBoxFreq.value()

    def on_bandwidth_changed(self):
        self.bandwidth = self.ui.spinBoxBandwidth.value()

    def on_gain_changed(self):
        self.gain = self.ui.spinBoxGain.value()

    def on_path_edited(self):
        self.set_path(self.ui.lineEdit_Path.text())

    def on_description_changed(self):
        self.description = self.ui.txtEdDescription.toPlainText()

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

        self.commited = True
        self.close()

    @pyqtSlot(QTableWidgetItem)
    def on_participant_item_changed(self, item: QTableWidgetItem):
        row, col = item.row(), item.column()
        if row < len(self.participants) and row >= 0:
            if col == 0:
                self.participants[row].name = item.text()
            elif col == 1:
                self.participants[row].shortname = item.text()
            elif col == 2:
                self.participants[row].address_hex = item.text()

    def set_path(self, path):
        self.path = path
        self.ui.lineEdit_Path.setText(self.path)
        name = os.path.basename(os.path.normpath(self.path))
        self.ui.lblName.setText(name)

        self.ui.lblNewPath.setVisible(not os.path.isdir(self.path))

    def on_btn_select_path_clicked(self):
        directory = FileOperator.get_directory()
        if directory:
            self.set_path(directory)

    @pyqtSlot(str)
    def on_spectrum_analyzer_link_activated(self, link: str):
        if link == "open_spectrum_analyzer":
            r = SendRecvDialogController(433.92e6, 1e6, 1e6, 20, "", Mode.spectrum, parent=self)
            if r.has_empty_device_list:
                Errors.no_device()
                r.close()
                return

            r.recording_parameters.connect(self.set_params_from_spectrum_analyzer)
            r.show()

    def set_params_from_spectrum_analyzer(self, freq: str, sample_rate: str, bw: str, gain: str, dev_name: str):
       self.ui.spinBoxFreq.setValue(float(freq))
       self.ui.spinBoxSampleRate.setValue(float(sample_rate))
       self.ui.spinBoxBandwidth.setValue(float(bw))
       self.ui.spinBoxGain.setValue(int(gain))


    def on_btn_add_participant_clicked(self):
        used_shortnames = {p.shortname for p in self.participants}
        nchars = 0
        participant = None
        while participant is None:
            nchars += 1
            for c in string.ascii_uppercase:
                shortname = nchars * str(c)
                if shortname not in used_shortnames:
                    participant = Participant("Device "+shortname, shortname)
                    break

        self.participants.append(participant)
        self.__write_participants_to_table()
        self.ui.btnRemoveParticipant.setEnabled(True)

    def on_btn_remove_participant_clicked(self):
        if len(self.participants) <= 1:
            return

        try:
            srange = self.ui.tblParticipants.selectedRanges()[0]
            start, end = srange.topRow(), srange.bottomRow()
        except IndexError: #nothing selected
            start, end = len(self.participants) - 1, len(self.participants) - 1 # delete last element

        if end - start >= len(self.participants) - 1:
            # Ensure one left
            start += 1

        del self.participants[start:end+1]
        self.__write_participants_to_table()
        self.ui.btnRemoveParticipant.setDisabled(len(self.participants) <= 1)
