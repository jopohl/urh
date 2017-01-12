from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItemGroup
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt

class SimulatorScene(QGraphicsScene):
    def __init__(self, parent=None, controller=None, participants=None):
        super().__init__(parent)
        self.controller = controller
        self.participants = participants
        self.participants_dict = {}

    def draw_participants(self, participants):
        participants_count = len(participants)
        # step = self.sceneRect().width() / (participants_count + 1)
        # height = self.sceneRect().height()

        step = 200

        if len(self.controller.messages) == 0:
            height = 50
        else:
            height = 50 * len(self.controller.messages)

        for key, part_group in self.participants_dict.items():
            for child in part_group.childItems():
                self.removeItem(child)
            self.destroyItemGroup(part_group);

        self.participants_dict = {}

        if participants_count < 2:
            return

        for i, participant in enumerate(participants):
            text = QGraphicsTextItem(participant.shortname)
            text.setPos((i + 1)*step - (text.boundingRect().width() / 2), 0)
            line = QGraphicsLineItem((i + 1)*step, 30, (i + 1)*step, height)
            line.setPen(QPen(Qt.black, 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
            part_group = QGraphicsItemGroup()
            part_group.addToGroup(line)
            part_group.addToGroup(text)
            self.addItem(part_group)
            self.participants_dict[participant] = part_group