import numpy
from PyQt5.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QDialog, QApplication, QInputDialog

from urh import constants
from urh.models.PLabelTableModel import PLabelTableModel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.ui.delegates.CheckBoxDelegate import CheckBoxDelegate
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.DeleteButtonDelegate import DeleteButtonDelegate
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_properties_dialog import Ui_DialogLabels


class ProtocolLabelController(QDialog):
    def __init__(self, preselected_index, proto_group: ProtocolGroup, offset: int, viewtype: int,
                 parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogLabels()
        self.ui.setupUi(self)
        self.model = PLabelTableModel(proto_group, offset)
        self.preselected_index = preselected_index

        if proto_group.num_blocks > 0:
            maxval = numpy.max([len(block) for block in proto_group.decoded_bits_str])
        else:
            maxval = 42000

        self.ui.tblViewProtoLabels.setItemDelegateForColumn(1, SpinBoxDelegate(1, maxval, self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(2, SpinBoxDelegate(1, maxval, self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(3, CheckBoxDelegate(self))

        self.ui.tblViewProtoLabels.setItemDelegateForColumn(5,
                                                            ComboBoxDelegate([""] * len(constants.LABEL_COLORS),
                                                                             colors=constants.LABEL_COLORS,
                                                                             parent=self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(6, CheckBoxDelegate(self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(7, DeleteButtonDelegate(self))

        self.ui.tblViewProtoLabels.setModel(self.model)
        self.ui.tblViewProtoLabels.selectRow(preselected_index)

        for i in range(self.model.row_count):
            self.openEditors(i)

        self.ui.tblViewProtoLabels.resizeColumnsToContents()
        self.setWindowTitle(self.tr("Edit Protocol Labels from %s") % proto_group.name)

        self.create_connects()
        self.ui.cbProtoView.setCurrentIndex(viewtype)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def create_connects(self):
        self.ui.btnConfirm.clicked.connect(self.confirm)
        self.ui.cbProtoView.currentIndexChanged.connect(self.set_view_index)
        self.model.restrictive_changed.connect(self.handle_restrictive_changed)
        self.ui.tblViewProtoLabels.clicked.connect(self.on_table_clicked)

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

    @pyqtSlot(int, bool)
    def handle_restrictive_changed(self, row: int, restrictive: bool):
        self.model.update()

    @pyqtSlot(int)
    def set_view_index(self, ind):
        self.model.proto_view = ind
        self.model.update()

    @pyqtSlot(QModelIndex)
    def on_table_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        i = index.row()
        lbl = self.model.protocol_labels[i]
        j = index.column()
        if j == 4 and lbl.restrictive:
            seqs, indexes = self.model.get_protocol_sequences(lbl.start, lbl.end)
            item, ok = QInputDialog.getItem(self, "Choose matching pattern", "Pattern", seqs)
            if ok and item:
                self.model.set_refblock(lbl, indexes[seqs.index(item)])
                self.model.update()
