import math

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFontMetrics, QBrush
from PyQt5.QtWidgets import QStyledItemDelegate, QToolButton

from urh.ui.views.MessageTypeTableView import MessageTypeTableView
from urh.util import util


class MessageTypeButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        assert isinstance(parent, MessageTypeTableView)
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        button = QToolButton(parent)
        button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        num_rules = self.parent().model().get_num_active_rules_of_message_type_at(index.row())

        if num_rules == 0:
            icon = QIcon.fromTheme("configure")
        else:
            icon = self.draw_indicator(indicator=num_rules)

        button.setIcon(icon)
        button.setText("...")
        button.clicked.connect(self.on_btn_clicked)
        return button

    @staticmethod
    def draw_indicator(indicator: int):
        pixmap = QPixmap(24, 24)

        painter = QPainter(pixmap)
        w, h = pixmap.width(), pixmap.height()

        painter.fillRect(0, 0, w, h, QBrush((QColor(0, 0, 200, 255))))

        pen = QPen(QColor("white"))
        pen.setWidth(2)
        painter.setPen(pen)

        font = util.get_monospace_font()
        font.setBold(True)
        font.setPixelSize(16)
        painter.setFont(font)

        f = QFontMetrics(painter.font())
        indicator_str = str(indicator) if indicator < 10 else "+"

        fw = f.width(indicator_str)
        fh = f.height()
        painter.drawText(math.ceil(w / 2 - fw / 2), math.ceil(h / 2 + fh / 4), indicator_str)

        painter.end()
        return QIcon(pixmap)

    @pyqtSlot()
    def on_btn_clicked(self):
        button = self.sender()
        index = self.parent().indexAt(button.pos())
        if index.isValid():
            self.parent().configure_message_type_rules_triggered.emit(index.row())
