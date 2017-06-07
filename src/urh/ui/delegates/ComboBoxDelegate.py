import sys
from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, pyqtSlot
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap, QFontMetrics
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QComboBox


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, colors=None, is_editable=False, return_index=True, parent=None):
        """

        :param items:
        :param colors:
        :param is_editable:
        :param return_index: True for returning current index, false for returning current text of editor
        :param parent:
        """
        super().__init__(parent)
        self.items = items
        self.colors = colors
        self.return_index = return_index
        self.is_editable = is_editable
        self.current_edit_text = ""

        if colors:
            assert len(items) == len(colors)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = QComboBox(parent)
        if sys.platform == "win32":
            # Ensure text entries are visible with windows combo boxes
            editor.setMinimumHeight(self.sizeHint(option, index).height() + 10)

        editor.addItems(self.items)

        if self.is_editable:
            editor.setEditable(True)
            editor.setInsertPolicy(QComboBox.NoInsert)

        if self.current_edit_text:
            editor.setEditText(self.current_edit_text)

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
        editor.editTextChanged.connect(self.on_edit_text_changed)
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
        if self.return_index:
            model.setData(index, editor.currentIndex(), Qt.EditRole)
        else:
            model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

    @pyqtSlot(str)
    def on_edit_text_changed(self, text: str):
        self.current_edit_text = text
