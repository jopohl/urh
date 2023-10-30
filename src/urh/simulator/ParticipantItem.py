from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem

from urh import settings
from urh.signalprocessing.Participant import Participant


class ParticipantItem(QGraphicsItem):
    def __init__(self, model_item: Participant, parent=None):
        super().__init__(parent)

        self.model_item = model_item

        self.text = QGraphicsTextItem(self)

        self.line = QGraphicsLineItem(self)
        self.line.setPen(QPen(Qt.darkGray, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

        self.refresh()

    def update_position(self, x_pos=-1, y_pos=-1):
        if x_pos == -1:
            x_pos = self.x_pos()

        if y_pos == -1:
            y_pos = self.line.line().y2()

        self.text.setPos(x_pos - (self.text.boundingRect().width() / 2), 0)
        self.line.setLine(x_pos, 30, x_pos, y_pos)

    def x_pos(self):
        return self.line.line().x1()

    def width(self):
        return self.boundingRect().width()

    def refresh(self):
        self.text.setPlainText(
            "?" if not self.model_item else self.model_item.shortname
        )
        if hasattr(self.model_item, "simulate") and self.model_item.simulate:
            font = QFont()
            font.setBold(True)
            self.text.setFont(font)
            self.text.setDefaultTextColor(Qt.darkGreen)
            self.line.setPen(
                QPen(Qt.darkGreen, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            )
        else:
            self.text.setFont(QFont())
            self.text.setDefaultTextColor(settings.LINECOLOR)
            self.line.setPen(
                QPen(Qt.darkGray, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin)
            )

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget):
        pass
