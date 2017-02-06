from PyQt5.QtWidgets import QGraphicsView, QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, pyqtSlot

class SimulatorGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.delete_action = QAction(self.tr("Delete selection"), self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.on_delete_action_triggered)
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.delete_action)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        self.scene().delete_selected_items()