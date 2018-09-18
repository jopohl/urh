from PyQt5.QtCore import pyqtSlot, QSize, Qt, QRectF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFontMetrics
from PyQt5.QtWidgets import QStyledItemDelegate, QToolButton, QApplication, QWidget, QHBoxLayout

from urh.ui.views.MessageTypeTableView import MessageTypeTableView
from urh.util import util


class MessageTypeButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        assert isinstance(parent, MessageTypeTableView)
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        button = QToolButton(parent)
        button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        if QIcon.hasThemeIcon("configure"):
            icon = QIcon.fromTheme("configure")
            icon = self.draw_indicator(icon, self.parent().model().get_num_active_rules_of_message_type_at(index.row()))
            button.setIcon(icon)
        else:
            button.setText("...")

        button.clicked.connect(self.on_btn_clicked)
        return button

    def draw_indicator(self, icon: QIcon, indicator: int):
        if indicator == 0:
            return icon

        pixmap = icon.pixmap(icon.actualSize(QSize(25, 25)))

        painter = QPainter(pixmap)
        w, h = pixmap.width(), pixmap.height()

        painter.setPen(Qt.transparent)
        painter.setBrush(QColor(0, 0, 255, 150))
        painter.drawEllipse(QRectF(w/3, h/3, 2*w/3, 2*h/3))

        pen = QPen(QColor("white"))
        pen.setWidth(2)
        painter.setPen(pen)

        font = util.get_monospace_font()
        font.setBold(True)
        painter.setFont(font)

        f = QFontMetrics(painter.font())
        indicator_str = str(indicator) if indicator < 10 else "+"

        fw = f.width(indicator_str)
        fh = f.height()
        painter.drawText(w - fw - 2, fh, indicator_str)

        painter.end()
        return QIcon(pixmap)

    @pyqtSlot()
    def on_btn_clicked(self):
        button = self.sender()
        index = self.parent().indexAt(button.pos())
        if index.isValid():
            self.parent().configure_message_type_rules_triggered.emit(index.row())
