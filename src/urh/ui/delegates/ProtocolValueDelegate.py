from PyQt5.QtCore import QModelIndex, QAbstractItemModel, Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QLineEdit, QHBoxLayout, \
    QCompleter, QLabel, QSpinBox, QDirModel

from urh.ui.ExpressionLineEdit import ExpressionLineEdit
from urh.ui.RuleExpressionValidator import RuleExpressionValidator


class ExternalProgramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.line_edit_external_program = QLineEdit()
        self.line_edit_external_program.setCompleter(completer)
        self.line_edit_external_program.setPlaceholderText("Type in a path to external program.")

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.line_edit_external_program)

        self.setLayout(self.layout)


class RandomValueWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAutoFillBackground(True)

        self.lbl_random_min = QLabel("Minimum (Decimal):")
        self.lbl_random_max = QLabel("Maximum (Decimal):")
        self.spinbox_random_min = QSpinBox()
        self.spinbox_random_max = QSpinBox()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.lbl_random_min)
        self.layout.addWidget(self.spinbox_random_min)
        self.layout.addWidget(self.lbl_random_max)
        self.layout.addWidget(self.spinbox_random_max)

        self.spinbox_random_max.valueChanged.connect(self.on_max_value_changed)

        self.setLayout(self.layout)

    def on_max_value_changed(self, value):
        self.spinbox_random_min.setMaximum(value - 1)


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
            random_widget.spinbox_random_min.setMaximum(lbl.fuzz_maximum - 2)
            random_widget.spinbox_random_max.setMinimum(1)
            random_widget.spinbox_random_max.setMaximum(lbl.fuzz_maximum - 1)

            return random_widget
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        if isinstance(editor, ExternalProgramWidget):
            item = index.model().data(index)
            editor.line_edit_external_program.setText(item)
        elif isinstance(editor, RandomValueWidget):
            items = index.model().data(index, Qt.EditRole)
            editor.spinbox_random_max.setValue(items[1])
            editor.spinbox_random_min.setValue(items[0])
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        if isinstance(editor, ExternalProgramWidget):
            model.setData(index, editor.line_edit_external_program.text(), Qt.EditRole)
        elif isinstance(editor, RandomValueWidget):
            model.setData(index, [editor.spinbox_random_min.value(), editor.spinbox_random_max.value()], Qt.EditRole)
        else:
            super().setModelData(editor, model, index)
