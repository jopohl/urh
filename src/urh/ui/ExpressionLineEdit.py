from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QValidator
import html

from urh.ui.RuleExpressionValidator import RuleExpressionValidator

class ExpressionLineEdit(QLineEdit):
    fld_abbrev_chars = ".0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"

    def __init__(self, parent=None):
        super().__init__(parent)

    def setCompleter(self, completer):
        self.completer = completer

        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def setValidator(self, validator: RuleExpressionValidator):
        validator.validation_status_changed.connect(self.on_validation_status_changed)
        super().setValidator(validator)

    def on_validation_status_changed(self, status, message):
        style_sheet = 'QLineEdit { background-color: rgba(255, 175, 175) }' if status == QValidator.Intermediate else ''
        message = html.escape(message)
        self.setToolTip("<pre>" + message + "</pre>")
        self.setStyleSheet(style_sheet)

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