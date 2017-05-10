from urh.signalprocessing.GraphicsItem import GraphicsItem
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

from urh import constants

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QGraphicsTextItem

class LabelItem(GraphicsItem):
    def __init__(self, scene_mode: int, model_item: SimulatorProtocolLabel, parent=None):
        assert isinstance(model_item, SimulatorProtocolLabel)

        if scene_mode == 0:
            super().__init__(model_item=model_item, parent=parent)
        else:
            super().__init__(model_item=model_item, is_selectable=True, accept_hover_events=True, parent=parent)

        self.name = QGraphicsTextItem(self)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        self.name.setFont(font)

        self.refresh()

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