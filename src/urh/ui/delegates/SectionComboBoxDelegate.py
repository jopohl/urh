import sys
from collections import OrderedDict

from PyQt5.QtCore import QModelIndex, pyqtSlot, QAbstractItemModel, Qt
from PyQt5.QtGui import QPainter, QStandardItem
from PyQt5.QtWidgets import QItemDelegate, QStyleOptionViewItem, QStyle, QComboBox, QStyledItemDelegate, QWidget


class SectionItemDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item_type = index.data(Qt.AccessibleDescriptionRole)
        if item_type == "parent":
            parent_option = option
            parent_option.state |= QStyle.State_Enabled
            super().paint(painter, parent_option, index)
        elif item_type == "child":
            child_option = option
            indent = option.fontMetrics.width(4 * " ")
            child_option.rect.adjust(indent, 0, 0, 0)
            child_option.textElideMode = Qt.ElideNone
            super().paint(painter, child_option, index)
        else:
            super().paint(painter, option, index)


class SectionComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def add_parent_item(self, text):
        item = QStandardItem(text)
        item.setFlags(item.flags() & ~(Qt.ItemIsEnabled | Qt.ItemIsSelectable))
        item.setData("parent", Qt.AccessibleDescriptionRole)

        font = item.font()
        font.setBold(True)
        item.setFont(font)

        self.model().appendRow(item)

    def add_child_item(self, text):
        item = QStandardItem(text)
        item.setData("child", Qt.AccessibleDescriptionRole)
        self.model().appendRow(item)


class SectionComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items: OrderedDict, parent=None):
        """

        :param items:
        :param parent:
        """
        super().__init__(parent)
        self.items = items

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = SectionComboBox(parent)
        editor.setItemDelegate(SectionItemDelegate(editor.itemDelegate().parent()))
        if sys.platform == "win32":
            # Ensure text entries are visible with windows combo boxes
            editor.setMinimumHeight(self.sizeHint(option, index).height() + 10)

        for title, items in self.items.items():
            editor.add_parent_item(title)
            for item in items:
                editor.add_child_item(item)
        editor.currentIndexChanged.connect(self.current_index_changed)
        return editor

    def setEditorData(self, editor: SectionComboBox, index: QModelIndex):
        editor.blockSignals(True)
        item = index.model().data(index)
        editor.setCurrentText(item)
        editor.blockSignals(False)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor.setGeometry(option.rect)

    @pyqtSlot()
    def current_index_changed(self):
        self.commitData.emit(self.sender())
