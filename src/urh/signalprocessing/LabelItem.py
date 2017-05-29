from urh.signalprocessing.GraphicsItem import GraphicsItem
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

from urh import constants

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont, QColor
from PyQt5.QtWidgets import QGraphicsTextItem

class LabelItem(GraphicsItem):
    font_bold_italic = None

    def __init__(self, model_item: SimulatorProtocolLabel, parent=None):
        assert isinstance(model_item, SimulatorProtocolLabel)
        super().__init__(model_item=model_item, parent=parent)

        self.name = QGraphicsTextItem(self)
        self.name.setFont(GraphicsItem.font)

    def update_flags(self):
        if self.scene().mode == 1:
            self.set_flags(is_selectable=True, accept_hover_events=True)

    def update_numbering(self):
        pass

    def paint(self, painter, option, widget):
        painter.setBrush(constants.LABEL_COLORS[self.model_item.color_index])
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)

    def boundingRect(self):
        return self.childrenBoundingRect()

    def refresh(self):
        self.name.setPlainText(self.model_item.name)