import numpy
from PyQt5.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QDialog, QApplication, QInputDialog

from urh import constants
from urh.models.PLabelTableModel import PLabelTableModel
from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.ui.delegates.CheckBoxDelegate import CheckBoxDelegate
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.DeleteButtonDelegate import DeleteButtonDelegate
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_properties_dialog import Ui_DialogLabels


class ProtocolLabelController(QDialog):
    def __init__(self, preselected_index, labelset: LabelSet, viewtype: int, max_end: int, block:ProtocolBlock, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogLabels()
        self.ui.setupUi(self)
        self.model = PLabelTableModel(labelset, block=block)
        self.preselected_index = preselected_index

        self.ui.tblViewProtoLabels.setItemDelegateForColumn(1, SpinBoxDelegate(1, max_end, self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(2, SpinBoxDelegate(1, max_end, self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(3,
                                                            ComboBoxDelegate([""] * len(constants.LABEL_COLORS),
                                                                             colors=constants.LABEL_COLORS,
                                                                             parent=self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(4, CheckBoxDelegate(self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(5, DeleteButtonDelegate(self))

        self.ui.tblViewProtoLabels.setModel(self.model)
        self.ui.tblViewProtoLabels.selectRow(preselected_index)

        for i in range(self.model.row_count):
            self.openEditors(i)

        self.ui.tblViewProtoLabels.resizeColumnsToContents()
        self.setWindowTitle(self.tr("Edit Protocol Labels from %s") % labelset.name)

        self.create_connects()
        self.ui.cbProtoView.setCurrentIndex(viewtype)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def create_connects(self):
        self.ui.btnConfirm.clicked.connect(self.confirm)
        self.ui.cbProtoView.currentIndexChanged.connect(self.set_view_index)

    @pyqtSlot()
    def confirm(self):
        self.close()

    def openEditors(self, row):
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 1))
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 2))
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 3))

        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 5))
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 6))
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 7))

    @pyqtSlot(int)
    def set_view_index(self, ind):
        self.model.proto_view = ind
        self.model.update()