from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QFileDialog, QLineEdit, QHBoxLayout, QToolButton, QCompleter
from PyQt5.QtCore import QModelIndex, QAbstractItemModel, QDir, Qt, pyqtSlot

from urh.ui.ExpressionLineEdit import ExpressionLineEdit
from urh.ui.RuleExpressionValidator import RuleExpressionValidator

class ExternalProgramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.extProgramLineEdit = QLineEdit()

        self.btnChooseExtProg = QToolButton()
        self.btnChooseExtProg.setText("...")
        self.btnChooseExtProg.clicked.connect(self.on_btn_choose_ext_prog_clicked)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.extProgramLineEdit)
        self.layout.addWidget(self.btnChooseExtProg)

        self.setLayout(self.layout)

    @pyqtSlot()
    def on_btn_choose_ext_prog_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose external program"), QDir.homePath())

        if file_name is not None and ok:
            self.extProgramLineEdit.setText(file_name)

class ProtocolValueDelegate(QStyledItemDelegate):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        row = index.row()

        if model.message_type[row].value_type_index == 2:
            line_edit = ExpressionLineEdit(parent)
            line_edit.setPlaceholderText("(item1.length + 3) ^ 0x12")
            line_edit.setCompleter(QCompleter(self.controller.completer_model, line_edit))
            line_edit.setValidator(RuleExpressionValidator(self.controller.sim_expression_parser))
            line_edit.setToolTip(self.controller.sim_expression_parser.formula_help)
            return line_edit
        elif model.message_type[row].value_type_index == 3:
            return ExternalProgramWidget(parent)
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