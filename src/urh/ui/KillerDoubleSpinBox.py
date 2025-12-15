import string

from PyQt6.QtCore import QLocale
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QDoubleSpinBox


class KillerDoubleSpinBox(QDoubleSpinBox):
    """
    Print values with suffix (G,M,K)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.auto_update_step_size = True

        self.lineEdit().setValidator(None)

        # Can't connect to value changed, as it would delete the number when changing a digit
        # see: https://github.com/jopohl/urh/issues/129
        self.editingFinished.connect(self.adjust_step)

    def setValue(self, value: float):
        super().setValue(value)
        self.adjust_step()

    def adjust_step(self):
        if not self.auto_update_step_size:
            return

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
        if abs(value) >= 10**9:
            result, suffix = super().textFromValue(value / 10**9), "G"
        elif abs(value) >= 10**6:
            result, suffix = super().textFromValue(value / 10**6), "M"
        elif abs(value) >= 10**3:
            result, suffix = super().textFromValue(value / 10**3), "K"
        else:
            result, suffix = super().textFromValue(value), ""

        result = result.rstrip("0")
        if len(result) == 0:
            return result

        if result[-1] not in string.digits:
            result += "0"

        return result + suffix

    def valueFromText(self, text: str):
        if text.endswith("G") or text.endswith("g"):
            return QLocale().toDouble(text[:-1])[0] * 10**9
        elif text.endswith("M") or text.endswith("m"):
            return QLocale().toDouble(text[:-1])[0] * 10**6
        elif text.endswith("K") or text.endswith("k"):
            return QLocale().toDouble(text[:-1])[0] * 10**3
        else:
            return QLocale().toDouble(text.rstrip(self.suffix()))[0]

    def validate(self, inpt: str, pos: int):
        if self.suffix().upper() in ("", "K", "M", "G"):
            rx = QRegularExpression("^(-?[0-9]+)[.]?[0-9]*[kKmMgG]?$")
        else:
            rx = QRegularExpression("^(-?[0-9]+)[.]?[0-9]*[{}]?$".format(self.suffix()))
        result = (
            QValidator.State.Acceptable
            if rx.match(inpt.replace(",", ".")).hasMatch()
            else QValidator.State.Invalid
        )
        return result, inpt, pos
