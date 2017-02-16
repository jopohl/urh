from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QDoubleSpinBox

class KillerDoubleSpinBox(QDoubleSpinBox):
    """
    Print values with suffix (G,M,K)
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lineEdit().setValidator(None)

        # Cant connect to value changed, as it would delete the number when changing a digit
        # see: https://github.com/jopohl/urh/issues/129
        self.editingFinished.connect(self.adjust_step)
        self.auto_suffix = True

    def setValue(self, value: float):
        super().setValue(value)
        self.adjust_step()

    def adjust_step(self):
        value = abs(self.value())
        if value >= 1e9:
            self.setSingleStep(10 ** (9 - self.decimals()))
        elif value >= 1e6:
            self.setSingleStep(10 ** (6 - self.decimals()))
        elif value >= 1e3:
            self.setSingleStep(10 ** (3 - self.decimals()))
        else:
            self.setSingleStep(10 ** -(self.decimals()))

    def textFromValue(self, value: float):
        if abs(value) >= 10 ** 9:
            return super().textFromValue(value / 10 ** 9) + "G"
        elif abs(value) >= 10 ** 6:
            return super().textFromValue(value / 10 ** 6) + "M"
        elif abs(value) >= 10 ** 3:
            return super().textFromValue(value / 10 ** 3) + "K"
        else:
            return super().textFromValue(value)

    def valueFromText(self, text: str):
        if text.endswith("G") or text.endswith("g"):
            return super().valueFromText(text[:-1]) * 10 ** 9
        elif text.endswith("M") or text.endswith("m"):
            return super().valueFromText(text[:-1]) * 10 ** 6
        elif text.endswith("K") or text.endswith("k"):
            return super().valueFromText(text[:-1]) * 10 ** 3
        else:
            return super().valueFromText(text)

    def validate(self, inpt: str, pos: int):
        rx = QRegExp("^(-?[0-9]+)[.]?[0-9]*[kKmMgG]?$")
        result = QValidator.Acceptable if rx.exactMatch(inpt.replace(",", ".")) else QValidator.Invalid
        return result, inpt, pos
