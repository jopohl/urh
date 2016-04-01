from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDropEvent

from urh.SignalSceneManager import SignalSceneManager
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView


class ZoomAndDropableGraphicView(ZoomableGraphicView):
    signal_loaded = pyqtSignal(ProtocolAnalyzer)

    def __init__(self, parent=None):
        self.scene_creator = None
        """:type: SignalSceneManager """
        self.signal_tree_root = None
        """type signal_tree_root: ProtocolTreeItem"""

        self.signal = None
        self.proto_analyzer = None

        super().__init__(parent)


    def dragEnterEvent(self, QDragEnterEvent):
        QDragEnterEvent.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mimedata = event.mimeData()
        data_str = str(mimedata.text())
        indexes = list(data_str.split("/")[:-1])

        signal = None
        proto_analyzer = None
        for index in indexes:
            row, column, parent = map(int, index.split(","))
            if parent == -1:
                parent = self.signal_tree_root
            else:
                parent = self.signal_tree_root.child(parent)
            node = parent.child(row)
            if node.protocol is not None and node.protocol.signal is not None:
                signal = node.protocol.signal
                proto_analyzer = node.protocol
                break

        if signal is None:
            return

        self.draw_signal(signal, proto_analyzer)

    def draw_signal(self, signal, proto_analyzer):
        if signal is None:
            return

        self.horizontalScrollBar().blockSignals(True)

        self.scene_creator = SignalSceneManager(signal, self)
        self.scene_creator.init_scene()
        self.setScene(self.scene_creator.scene)
        self.scene_creator.show_full_scene()
        self.fitInView(self.sceneRect())
        self.signal_loaded.emit(proto_analyzer)
        self.signal = signal
        self.proto_analyzer = proto_analyzer

        self.horizontalScrollBar().blockSignals(False)


    def handle_signal_zoomed_or_scrolled(self):
        if self.scene_creator is not None:
            x1 = self.view_rect().x()
            x2 = x1 + self.view_rect().width()
            self.scene_creator.show_scene_section(x1, x2)
