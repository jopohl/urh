from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import QDialog, QHeaderView

from urh import constants
from urh.models.PLabelTableModel import PLabelTableModel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.delegates.CheckBoxDelegate import CheckBoxDelegate
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_properties_dialog import Ui_DialogLabels


class ProtocolLabelController(QDialog):
    apply_decoding_changed = pyqtSignal(ProtocolLabel, MessageType)

    def __init__(self, preselected_index, message: Message, viewtype: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogLabels()
        self.ui.setupUi(self)
        field_types = FieldType.load_from_xml()
        self.model = PLabelTableModel(message, field_types)
        self.preselected_index = preselected_index

        self.ui.tblViewProtoLabels.setItemDelegateForColumn(0, ComboBoxDelegate([ft.caption for ft in field_types],
                                                                                is_editable=True,
                                                                                return_index=False, parent=self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(1, SpinBoxDelegate(1, len(message), self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(2, SpinBoxDelegate(1, len(message), self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(3,
                                                            ComboBoxDelegate([""] * len(constants.LABEL_COLORS),
                                                                             colors=constants.LABEL_COLORS,
                                                                             parent=self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(4, CheckBoxDelegate(self))

        self.ui.tblViewProtoLabels.setModel(self.model)
        self.ui.tblViewProtoLabels.selectRow(preselected_index)

        self.ui.tblViewProtoLabels.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.tblViewProtoLabels.resizeColumnsToContents()
        self.setWindowTitle(self.tr("Edit Protocol Labels from %s") % message.message_type.name)

        self.create_connects()
        self.ui.cbProtoView.setCurrentIndex(viewtype)
        self.setAttribute(Qt.WA_DeleteOnClose)

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

        for i in range(self.model.rowCount()):
            self.open_editors(i)

    def create_connects(self):
        self.ui.btnConfirm.clicked.connect(self.confirm)
        self.ui.cbProtoView.currentIndexChanged.connect(self.set_view_index)
        self.model.apply_decoding_changed.connect(self.on_apply_decoding_changed)

    def open_editors(self, row):
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 3))
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 4))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Enter:
            event.ignore()
        else:
            event.accept()

    def closeEvent(self, event: QCloseEvent):
        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    @pyqtSlot()
    def confirm(self):
        self.close()

    @pyqtSlot(int)
    def set_view_index(self, ind):
        self.model.proto_view = ind
        self.model.update()

    @pyqtSlot(ProtocolLabel)
    def on_apply_decoding_changed(self, lbl: ProtocolLabel):
        self.apply_decoding_changed.emit(lbl, self.model.message_type)
