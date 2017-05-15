from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QFont, QFontDatabase

from urh.signalprocessing.SimulatorGotoAction import SimulatorGotoAction
from urh.signalprocessing.SimulatorProgramAction import SimulatorProgramAction
from urh.signalprocessing.GraphicsItem import GraphicsItem
from urh.signalprocessing.SimulatorItem import SimulatorItem

class ActionItem(GraphicsItem):
    def __init__(self, model_item: SimulatorItem, parent=None):
        super().__init__(model_item=model_item, parent=parent)

        self.text = QGraphicsTextItem(self)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        #font.setWeight(QFont.DemiBold)
        self.text.setFont(font)

    def update_flags(self):
        if self.scene().mode == 0:
            self.set_flags(is_selectable=True, is_movable=True, accept_hover_events=True, accept_drops=True)
        else:
            self.set_flags(is_selectable=True, accept_hover_events=True)

    def update_position(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)
        start_x = (self.scene().items_width() - self.labels_width()) / 2
        self.number.setPos(start_x, 0)
        start_x += self.number.boundingRect().width()
        self.text.setPos(start_x, 0)
        super().update_position(x_pos, y_pos)

    def labels_width(self):
        width = self.number.boundingRect().width()
        #width += 5
        width += self.text.boundingRect().width()
        return width

class GotoActionItem(ActionItem):
    def __init__(self, model_item: SimulatorGotoAction, parent=None):
        assert isinstance(model_item, SimulatorGotoAction)
        super().__init__(model_item=model_item, parent=parent)

    def refresh(self):
        if self.model_item.goto_target:
            self.text.setPlainText("GOTO: " + self.model_item.goto_target)
        else:
            self.text.setPlainText("GOTO: ...")

class ProgramActionItem(ActionItem):
    def __init__(self, model_item: SimulatorItem, parent=None):
        assert isinstance(model_item, SimulatorProgramAction)
        super().__init__(model_item=model_item, parent=parent)
        self.text.setPlainText("Start program [/usr/bin/test]")