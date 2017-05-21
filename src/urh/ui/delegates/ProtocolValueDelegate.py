from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QFileDialog, QLineEdit, QHBoxLayout, QToolButton, QCompleter
from PyQt5.QtCore import QModelIndex, QAbstractItemModel, QDir, Qt, pyqtSlot, QStringListModel

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

class FormulaLineEdit(QLineEdit):
    fld_abbrev_chars = ".0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"

    def __init__(self, completer_strings, parent=None):
        super().__init__(parent)
        
        self.completer_model = QStringListModel(completer_strings, self)
        self.setCompleter(QCompleter(self.completer_model, self))

    def setCompleter(self, completer):
        self.completer = completer

        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        start, end = self.get_token_under_cursor()
        token_word = self.text()[start:end]

        self.completer.setCompletionPrefix(token_word)

        if (len(token_word) < 1 or (self.completer.completionCount() == 1 and
                self.completer.currentCompletion() == token_word)):
            self.completer.popup().hide()
            return

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                    self.completer.popup().verticalScrollBar().sizeHint().width())

        self.completer.complete(cr)

    def get_token_under_cursor(self):
        if self.selectionStart() >= 0:
            return (0, 0)

        start = self.cursorPosition()
        end = start

        while start > 0 and self.text()[start - 1] in self.fld_abbrev_chars:
            start -= 1

        while end < len(self.text()) and self.text()[end] in self.fld_abbrev_chars:
            end += 1

        return (start, end)

    def insert_completion(self, completion_text):
        start, end = self.get_token_under_cursor()
        new_text = self.text()[:start] + completion_text + self.text()[end:]
        self.setText(new_text)
        self.setCursorPosition(start + len(completion_text))

class ProtocolValueDelegate(QStyledItemDelegate):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        row = index.row()

        if model.message_type[row].value_type_index == 2:
            return FormulaLineEdit(self.controller.sim_expression_parser.label_list, parent)
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