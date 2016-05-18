import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QCompleter, QDirModel

from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import Mode
from urh.ui.ui_project import Ui_ProjectDialog
from urh.util import FileOperator
from urh.util.Errors import Errors


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

        self.ui.lineEdit_Path.textEdited.connect(self.on_path_edited)
        self.ui.btnOK.clicked.connect(self.on_button_ok_clicked)
        self.ui.btnSelectPath.clicked.connect(self.on_btn_select_path_clicked)
        self.ui.lOpenSpectrumAnalyzer.linkActivated.connect(self.on_spectrum_analyzer_link_activated)

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