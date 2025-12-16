from PyQt6.QtWidgets import QGraphicsTextItem
from PyQt6.QtGui import QFontDatabase


class UnlabeledRangeItem(QGraphicsTextItem):
    def __init__(self, parent):
        super().__init__(parent)

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(8)
        self.setFont(font)
        self.setPlainText("...")
