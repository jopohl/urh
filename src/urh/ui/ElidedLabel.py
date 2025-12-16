from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QLabel


class ElidedLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_text = ""

    def __set_elided_text(self):
        fm = QFontMetrics(self.font())
        super().setText(
            fm.elidedText(self.full_text, Qt.TextElideMode.ElideRight, self.width())
        )

        self.setToolTip(self.full_text)

    def setText(self, text: str):
        self.full_text = text
        self.__set_elided_text()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.__set_elided_text()

    def minimumSizeHint(self) -> QSize:
        return QSize(0, super().minimumSizeHint().height())
