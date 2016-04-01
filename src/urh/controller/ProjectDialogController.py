import os

from PyQt5.QtWidgets import QDialog, QCompleter, QDirModel

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
        self.ui.spinBoxFreq.valueChanged.connect(self.on_frequency_edited)
        self.ui.spinBoxSampleRate.valueChanged.connect(self.on_sample_rate_edited)
        self.ui.lineEdit_Path.textEdited.connect(self.on_path_edited)
        self.ui.btnOK.clicked.connect(self.on_button_ok_clicked)
        self.ui.btnSelectPath.clicked.connect(self.on_btn_select_path_clicked)

    def on_sample_rate_edited(self):
        self.sample_rate = self.ui.spinBoxSampleRate.value()

    def on_frequency_edited(self):
        self.freq = self.ui.spinBoxFreq.value()

    def on_path_edited(self):
        self.set_path(self.ui.lineEdit_Path.text())

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
