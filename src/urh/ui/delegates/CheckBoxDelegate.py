from PyQt5.QtCore import QModelIndex, QAbstractItemModel, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QWidget,
    QStyleOptionViewItem,
    QCheckBox,
)


class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = True

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ):
        editor = QCheckBox(parent)
        editor.stateChanged.connect(self.stateChanged)
        return editor

    def setEditorData(self, editor: QCheckBox, index: QModelIndex):
        editor.blockSignals(True)
        editor.setChecked(index.model().data(index))
        self.enabled = editor.isChecked()
        editor.blockSignals(False)

    def setModelData(
        self, editor: QCheckBox, model: QAbstractItemModel, index: QModelIndex
    ):
        model.setData(index, editor.isChecked(), Qt.EditRole)

    @pyqtSlot()
    def stateChanged(self):
        self.commitData.emit(self.sender())
