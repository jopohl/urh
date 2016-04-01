from PyQt5.QtCore import QRectF, QSizeF, QPointF, Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsLineItem

from urh import constants


class LabeledArrow(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, label):
        super().__init__(x1, y1, x2, y2)
        self.ItemIsMovable = False
        self.ItemIsSelectable = False
        self.ItemIsFocusable = False
        self.label = str(label)
        self.setPen(QPen(constants.ARROWCOLOR, Qt.FlatCap))

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        try:
            return QRectF(self.line().p1(), QSizeF(self.line().p2().x() - self.line().p1().x(),
                                                   self.line().p2().y() - self.line().p1().y())) \
                .normalized().adjusted(-extra, -extra, extra, extra)
        except RuntimeError:
            return QRectF(0,0,0,0)

    def paint(self, painter, QStyleOptionGraphicsItem, QWidget_widget=None):
        """

        @type painter: QPainter
        @param QStyleOptionGraphicsItem:
        @param QWidget_widget:
        @return:
        """
        painter.setPen(self.pen())
        x1 = self.line().x1()
        y1 = self.line().y1()
        y2 = self.line().y2()

        x_arrowSize = 10
        y_arrowSize = 0.1 * abs(y2 - y1)
        labelheight = 0.75 * abs(y2 - y1)

        painter.drawLine(QPointF(x1, y1), QPointF(x1, y1 + labelheight / 2))
        painter.drawLine(QPointF(x1, y1), QPointF(x1 + x_arrowSize / 4, y1 + y_arrowSize / 2))
        painter.drawLine(QPointF(x1, y1), QPointF(x1 - x_arrowSize / 4, y1 + y_arrowSize / 2))

        painter.drawLine(QPointF(x1, y2 - labelheight / 2), QPointF(x1, y2))
        painter.drawLine(QPointF(x1, y2), QPointF(x1 + x_arrowSize / 4, y2 - y_arrowSize / 2))
        painter.drawLine(QPointF(x1, y2), QPointF(x1 - x_arrowSize / 4, y2 - y_arrowSize / 2))

        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        fm = painter.fontMetrics()
        pixelsWide = fm.width(self.label)
        pixelsHigh = fm.height()
        scale_factor = (0.2 * labelheight) / fm.height()
        scale_factor = scale_factor if scale_factor > 0 else 0.0000000000000000001
        painter.scale(1, scale_factor)



        # print(y1, y2, pixelsHigh)

        painter.drawText(QPointF(x1 - pixelsWide / 2, (1 / scale_factor) * (y1 + y2) / 2 + pixelsHigh / 4), self.label)
        # painter.drawText(QPointF(x1 - pixelsWide/2, (y1+y2+pixelsHigh)/2), self.label)

        del painter
