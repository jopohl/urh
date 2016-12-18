from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, pyqtSlot
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap
from PyQt5.QtWidgets import QItemDelegate, QWidget, QStyleOptionViewItem, QComboBox


class ComboBoxDelegate(QItemDelegate):
    def __init__(self, items, colors=None, is_editable=False, parent=None):
        super().__init__(parent)
        self.items = items
        self.colors = colors
        self.is_editable = is_editable
        if colors:
            assert len(items) == len(colors)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = QComboBox(parent)
        editor.addItems(self.items)

        if self.is_editable:
            editor.setEditable(True)
            editor.setInsertPolicy(QComboBox.NoInsert)

        if self.colors:
            img = QImage(16, 16, QImage.Format_RGB32)
            painter = QPainter(img)

            painter.fillRect(img.rect(), Qt.black)
            rect = img.rect().adjusted(1, 1, -1, -1)
            for i, item in enumerate(self.items):
                color = self.colors[i]
                painter.fillRect(rect, QColor(color.red(), color.green(), color.blue(), 255))
                editor.setItemData(i, QPixmap.fromImage(img), Qt.DecorationRole)

            del painter
        editor.currentIndexChanged.connect(self.currentIndexChanged)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        editor.blockSignals(True)
        item = index.model().data(index)
        try:
            indx = self.items.index(item) if item in self.items else int(item)
            editor.setCurrentIndex(indx)
        except ValueError:
            pass
        editor.blockSignals(False)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        model.setData(index, editor.currentIndex(), Qt.EditRole)

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
