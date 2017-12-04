from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QFontDatabase

class UnlabeledRangeItem(QGraphicsTextItem):
    def __init__(self, parent):
        super().__init__(parent)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        self.setFont(font)
        self.setPlainText("...")