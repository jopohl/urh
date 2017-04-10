from urh.signalprocessing.SimulatorGraphicsItem import SimulatorGraphicsItem
from urh.signalprocessing.MessageItem import MessageItem
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

from urh import constants

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QGraphicsTextItem

class LabelItem(SimulatorGraphicsItem):
    def __init__(self, model_item: SimulatorProtocolLabel, parent: MessageItem):
        super().__init__(model_item, parent)
        assert isinstance(model_item, SimulatorProtocolLabel)
        assert isinstance(parent, MessageItem)

        self.name = QGraphicsTextItem(self)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        self.name.setFont(font)

        self.refresh()

    def paint(self, painter, option, widget):
        painter.setBrush(constants.LABEL_COLORS[self.model_item.color_index])
        painter.drawRect(self.boundingRect())

    def boundingRect(self):
        return self.childrenBoundingRect()

    def refresh(self):
        self.name.setPlainText(self.model_item.name)