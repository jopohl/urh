from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent

from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.ui.ui_protocol_label import Ui_ProtocolLabelDialog

class ProtocolLabelDialog(QDialog):
    def __init__(self, label: SimulatorProtocolLabel, parent=None):
        super().__init__(parent)
        self.ui = Ui_ProtocolLabelDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.label = label

        self.ui.comboBoxName.addItems([ft.caption for ft in parent.field_types])
        self.ui.comboBoxName.setEditText(label.name)

        self.ui.spinBoxLabelStart.setValue(label.start + 1)
        self.ui.spinBoxLabelEnd.setValue(label.end)

        self.create_connects()

    def create_connects(self):
        self.ui.spinBoxLabelStart.valueChanged.connect(self.on_label_start_changed)
        self.ui.spinBoxLabelEnd.valueChanged.connect(self.on_label_end_changed)
        self.ui.comboBoxName.editTextChanged.connect(self.set_label_name)
        self.ui.comboBoxName.currentIndexChanged.connect(self.set_label_name)
        self.ui.btnSaveAndClose.clicked.connect(self.close)

    def on_label_start_changed(self, value: int):
        self.ui.spinBoxLabelEnd.setMinimum(self.ui.spinBoxLabelStart.value())
        self.label.start = value - 1

    def on_label_end_changed(self, value: int):
        self.ui.spinBoxLabelStart.setMaximum(self.ui.spinBoxLabelEnd.value())
        self.label.end = value

    def set_label_name(self):
        self.label.name = self.ui.comboBoxName.currentText()

    def closeEvent(self, event: QCloseEvent):
        self.parent().sim_proto_manager.label_updated.emit(self.label)
        super().closeEvent(event)