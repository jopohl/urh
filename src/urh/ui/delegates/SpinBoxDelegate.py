from PyQt5.QtCore import QModelIndex, pyqtSlot, QAbstractItemModel, Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QSpinBox


class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, minimum, maximum, parent=None, suffix=""):
        super().__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.suffix = suffix

    def _get_editor(self, parent) -> QSpinBox:
        return QSpinBox(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = self._get_editor(parent)
        editor.setMinimum(self.minimum)
        editor.setMaximum(self.maximum)
        editor.setSuffix(self.suffix)
        editor.valueChanged.connect(self.valueChanged)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        editor.blockSignals(True)
        try:
            editor.setValue(int(index.model().data(index)))
        except ValueError:
            pass # If Label was deleted and UI not updated yet
        editor.blockSignals(False)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        model.setData(index, editor.value(), Qt.EditRole)

    @pyqtSlot()
    def valueChanged(self):
        self.commitData.emit(self.sender())
