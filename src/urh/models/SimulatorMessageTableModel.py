from collections import defaultdict

from PyQt5.QtCore import QModelIndex, Qt

from urh.models.TableModel import TableModel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

class SimulatorMessageTableModel(TableModel):
    def __init__(self, parent=None):
        super().__init__(None, parent)
        self.protocol = ProtocolAnalyzer(None)

        self.decode = False

        self.label_mask = defaultdict(lambda: False)

    def update(self):
        self.refresh_label_mask()
        super().update()

    def refresh_label_mask(self):
        self.label_mask.clear()

        for i, message in enumerate(self.protocol.messages):
            for lbl in message.message_type:
                start, end = message.get_label_range(lbl, self.proto_view, self.decode)

                for j in range(start, end):
                    self.label_mask[i, j] = True

    def refresh_vertical_header(self):
        self.vertical_header_text.clear()

        for i, msg in enumerate(self.protocol.messages):
            participant_name = msg.participant.shortname if msg.participant else "?"
            destination_name = msg.destination.shortname if msg.destination else "?"

            self.vertical_header_text[i] = "{0} ({1} -> {2})".format(msg.index(), participant_name, destination_name)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i = index.row()
        j = index.column()

        if role == Qt.DisplayRole and self.display_data:
            if self.label_mask[i, j]:
                return "."

        return super().data(index, role)