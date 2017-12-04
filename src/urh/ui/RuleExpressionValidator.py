from PyQt5.QtGui import QValidator
from PyQt5.QtCore import pyqtSignal

class RuleExpressionValidator(QValidator):
    validation_status_changed = pyqtSignal(QValidator.State, str)

    def __init__(self, sim_expression_parser, is_formula=True, parent=None):
        super().__init__(parent)
        self.parser = sim_expression_parser
        self.is_formula = is_formula

    def validate(self, text, pos):
        valid, message, _ = self.parser.validate_expression(text, self.is_formula)
        state = QValidator.Acceptable if valid else QValidator.Intermediate

        self.validation_status_changed.emit(state, message)
        return (state, text, pos)