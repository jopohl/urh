from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import QRectF

from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorExternalProgramAction import SimulatorExternalProgramAction
from urh.simulator.GraphicsItem import GraphicsItem
from urh.simulator.SimulatorItem import SimulatorItem


class ActionItem(GraphicsItem):
    def __init__(self, model_item: SimulatorItem, parent=None):
        super().__init__(model_item=model_item, parent=parent)

        self.setFlag(QGraphicsTextItem.ItemIsPanel, True)

        self.text = QGraphicsTextItem(self)
        self.text.setFont(self.font)

    def update_flags(self):
        if self.scene().mode == 0:
            self.set_flags(is_selectable=True, is_movable=True, accept_hover_events=True, accept_drops=True)

    def update_position(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)
        start_x = (self.scene().items_width() - self.labels_width()) / 2
        self.number.setPos(start_x, 0)
        start_x += self.number.boundingRect().width()
        self.text.setPos(start_x, 0)

        width = self.scene().items_width()
        self.prepareGeometryChange()
        self.bounding_rect = QRectF(0, 0, width, self.childrenBoundingRect().height() + 5)

    def labels_width(self):
        width = self.number.boundingRect().width()
        width += self.text.boundingRect().width()
        return width


class GotoActionItem(ActionItem):
    def __init__(self, model_item: SimulatorGotoAction, parent=None):
        assert isinstance(model_item, SimulatorGotoAction)
        super().__init__(model_item=model_item, parent=parent)

    def refresh(self):
        text = "GOTO: "
        text += "..." if self.model_item.goto_target is None else self.model_item.goto_target
        self.text.setPlainText(text)


class ProgramActionItem(ActionItem):
    def __init__(self, model_item: SimulatorItem, parent=None):
        assert isinstance(model_item, SimulatorExternalProgramAction)
        super().__init__(model_item=model_item, parent=parent)
        self.text.setPlainText("External program")