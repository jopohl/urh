from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QFileDialog, QLineEdit, QHBoxLayout, QToolButton, QCompleter, QLabel, QSpinBox
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

class RandomValueWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAutoFillBackground(True)

        self.lblRandomMin = QLabel("Minimum (Decimal):")
        self.lblRandomMax = QLabel("Maximum (Decimal):")
        self.spinBoxRandomMin = QSpinBox()
        self.spinBoxRandomMax = QSpinBox()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.lblRandomMin)
        self.layout.addWidget(self.spinBoxRandomMin)
        self.layout.addWidget(self.lblRandomMax)
        self.layout.addWidget(self.spinBoxRandomMax)

        self.spinBoxRandomMax.valueChanged.connect(self.on_max_value_changed)

        self.setLayout(self.layout)

    def on_max_value_changed(self, value):
        self.spinBoxRandomMin.setMaximum(value - 1)

class ProtocolValueDelegate(QStyledItemDelegate):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        row = index.row()
        lbl = model.message_type[row]

        if lbl.value_type_index == 2:
            line_edit = ExpressionLineEdit(parent)
            line_edit.setPlaceholderText("(item1.length + 3) ^ 0x12")
            line_edit.setCompleter(QCompleter(self.controller.completer_model, line_edit))
            line_edit.setValidator(RuleExpressionValidator(self.controller.sim_expression_parser))
            line_edit.setToolTip(self.controller.sim_expression_parser.formula_help)
            return line_edit
        elif lbl.value_type_index == 3:
            return ExternalProgramWidget(parent)
        elif lbl.value_type_index == 4:
            random_widget = RandomValueWidget(parent)
            random_widget.spinBoxRandomMin.setMaximum(lbl.fuzz_maximum - 2)
            random_widget.spinBoxRandomMax.setMinimum(1)
            random_widget.spinBoxRandomMax.setMaximum(lbl.fuzz_maximum - 1)
            
            return random_widget
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        if isinstance(editor, ExternalProgramWidget):
            item = index.model().data(index)
            editor.extProgramLineEdit.setText(item)
        elif isinstance(editor, RandomValueWidget):
            items = index.model().data(index, Qt.EditRole)
            editor.spinBoxRandomMax.setValue(items[1])
            editor.spinBoxRandomMin.setValue(items[0])
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        if isinstance(editor, ExternalProgramWidget):
            model.setData(index, editor.extProgramLineEdit.text(), Qt.EditRole)
        elif isinstance(editor, RandomValueWidget):
            model.setData(index, [editor.spinBoxRandomMin.value(), editor.spinBoxRandomMax.value()], Qt.EditRole)
        else:
            super().setModelData(editor, model, index)