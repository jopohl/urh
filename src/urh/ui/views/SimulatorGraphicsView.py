from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import QRectF, Qt

class SimulatorGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_root_item = None
        self.controller = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        indexes = list(event.mimeData().text().split("/")[:-1])

        group_nodes = []
        file_nodes = []
        for index in indexes:
            try:
                row, column, parent = map(int, index.split(","))
                if parent == -1:
                    parent = self.tree_root_item
                else:
                    parent = self.tree_root_item.child(parent)
                node = parent.child(row)
                if node.is_group:
                    group_nodes.append(node)
                else:
                    file_nodes.append(node)
            except ValueError:
                continue

        # Which Nodes to add?
        nodes_to_add = []
        """:type: list of ProtocolTreeItem """
        for group_node in group_nodes:
            nodes_to_add.extend(group_node.children)
        nodes_to_add.extend([file_node for file_node in file_nodes if file_node not in nodes_to_add])
        protocols_to_add = [node.protocol for node in nodes_to_add]

        for protocol in protocols_to_add:
            self.controller.add_protocol(protocol)

        super().dropEvent(event)