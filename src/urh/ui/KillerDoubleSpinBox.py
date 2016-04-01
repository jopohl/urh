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
        self.lineEdit().textChanged.connect(self.on_text_changed)
        self.editingFinished.connect(self.on_text_edited)
        self.editingFinished.connect(self.adjust_step)
        self.valueChanged.connect(self.setUnit)
        self.auto_suffix = True

    def on_text_changed(self):
        text = self.lineEdit().text().upper()
        if text.endswith("G") or text.endswith("M") or text.endswith("K"):
            if self.suffix() != text[-1]:
                if self.auto_suffix:
                    self.setSuffix(text[-1])
                self.on_text_edited()
        else:
            if self.suffix() != "":
                if self.auto_suffix:
                    self.setSuffix("")
                self.on_text_edited()

    def on_text_edited(self):
        self.lineEdit().setText(self.lineEdit().text().upper())

    def setValue(self, val: float):
        super().setValue(val)
        self.adjust_step()


    def setUnit(self):
        value = abs(self.value())

        if 10 ** 9 <= value <= 10 ** 11:
            if self.suffix() != "G" and self.auto_suffix:
                self.setSuffix("G")
        elif 10 ** 6 <= value < 10 ** 9:
            if self.suffix() != "M" and self.auto_suffix:
                self.setSuffix("M")
        elif 10 ** 3 <= value < 10 ** 6:
            if self.suffix() != "K" and self.auto_suffix:
                self.setSuffix("K")
        else:
            if self.suffix() != "" and self.auto_suffix:
                self.setSuffix("")

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
            return super().textFromValue(value / 10 ** 9)
        elif abs(value) >= 10 ** 6:
            return super().textFromValue(value / 10 ** 6)
        elif abs(value) >= 10 ** 3:
            return super().textFromValue(value / 10 ** 3)
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
