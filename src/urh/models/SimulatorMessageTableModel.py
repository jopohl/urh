from collections import defaultdict

from PyQt5.QtCore import QModelIndex, Qt

from urh.models.TableModel import TableModel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

class SimulatorMessageTableModel(TableModel):
    def __init__(self, project_manager, parent=None):
        super().__init__(None, parent)
        self.protocol = ProtocolAnalyzer(None)

        self.project_manager = project_manager
        self.decode = False
        self.is_writeable = True

        self.label_mask = defaultdict(lambda: False)

    def update(self):
        self.refresh_label_mask()
        super().update()

    def refresh_label_mask(self):
        self.label_mask.clear()

        for i, message in enumerate(self.protocol.messages):
            for lbl in message.message_type:
                if lbl.value_type_index == 0:
                    continue

                start, end = message.get_label_range(lbl, self.proto_view, self.decode)

                for j in range(start, end):
                    self.label_mask[i, j] = True

    def refresh_vertical_header(self):
        self.vertical_header_text.clear()

        for i, msg in enumerate(self.protocol.messages):
            participant_name = msg.participant.shortname if msg.participant else "?"
            destination_name = msg.destination.shortname if msg.destination else "?"

            self.vertical_header_text[i] = "{0} ({1} -> {2})".format(msg.index(), participant_name, destination_name)

    def delete_range(self, msg_start: int, msg_end: int, index_start: int, index_end: int):
        removable_messages = []

        if msg_start > msg_end:
            msg_start, msg_end = msg_end, msg_start

        if index_start > index_end:
            index_start, index_end = index_end, index_start

        for i in range(msg_start, msg_end + 1):
            try:
                bs, be = self.protocol.convert_range(index_start, index_end, self.proto_view, 0, self.decode, message_indx=i)
                self.protocol.messages[i].clear_decoded_bits()
                del self.protocol.messages[i][bs:be + 1]

                if len(self.protocol.messages[i]) == 0:
                    removable_messages.append(self.protocol.messages[i])
            except IndexError:
                continue

        self.parent().simulator_config.delete_items(removable_messages)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i = index.row()
        j = index.column()

        if role == Qt.DisplayRole and self.display_data:
            if self.label_mask[i, j]:
                return "."

        return super().data(index, role)

    def flags(self, index: QModelIndex):
        if index.isValid():
            if self.is_writeable:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.NoItemFlags