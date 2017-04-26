from PyQt5.QtWidgets import QItemDelegate, QStyle, QStyleOptionViewItem, QComboBox, QWidget
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel, pyqtSlot
from PyQt5.QtGui import QStandardItem

class MessageComboBoxDelegate(QItemDelegate):
    def __init__(self, sim_proto_manager, parent=None):
        super().__init__(parent)
        self.sim_proto_manager = sim_proto_manager
        
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = QComboBox(parent)
        insert_separator = False

        editor.addItem("---Select label---", None)

        for message in self.sim_proto_manager.get_all_messages():
            for label in message.children:
                editor.addItem(message.index() + "::" + label.name, label)

        editor.currentIndexChanged.connect(self.currentIndexChanged)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        editor.blockSignals(True)
        item = index.model().data(index)

        indx = editor.findData(item)

        if indx != -1:
            editor.setCurrentIndex(indx)
        else:
            editor.setCurrentIndex(0)

        editor.blockSignals(False)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        model.setData(index, editor.itemData(editor.currentIndex()), Qt.EditRole)

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())