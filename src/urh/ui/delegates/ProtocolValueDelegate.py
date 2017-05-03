from PyQt5.QtWidgets import QItemDelegate, QWidget, QStyleOptionViewItem, QFileDialog, QLineEdit, QHBoxLayout, QToolButton
from PyQt5.QtCore import QModelIndex, QAbstractItemModel, QDir, Qt, pyqtSlot

class ExternalProgramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.extProgramLineEdit = QLineEdit()
        self.btnChooseExtProg = QToolButton()
        self.btnChooseExtProg.setText("...")

        self.btnChooseExtProg.clicked.connect(self.on_btn_choose_ext_prog_clicked)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.extProgramLineEdit)
        self.layout.addWidget(self.btnChooseExtProg)

        self.setLayout(self.layout)

    @pyqtSlot()
    def on_btn_choose_ext_prog_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose external program"), QDir.homePath())

        if file_name is not None and ok:
            self.extProgramLineEdit.setText(file_name)

class ProtocolValueDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        row = index.row()

        label = model.message_type[row]

        if label.value_type_index == 3:
            editor = ExternalProgramWidget(parent)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        if isinstance(editor, ExternalProgramWidget):
            item = index.model().data(index)
            editor.extProgramLineEdit.setText(item)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        if isinstance(editor, ExternalProgramWidget):
            model.setData(index, editor.extProgramLineEdit.text(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)