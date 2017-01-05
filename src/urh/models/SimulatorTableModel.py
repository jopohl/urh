from PyQt5.QtCore import QModelIndex, Qt

from urh import constants
from urh.models.TableModel import TableModel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

class SimulatorTableModel(TableModel):

    def __init__(self, proto_analyzer: ProtocolAnalyzer, participants, parent=None):
        super().__init__(participants=participants, parent=parent)

        self.protocol = proto_analyzer
        self.is_writeable = True
        self.decode = False

    def flags(self, index: QModelIndex):
        if index.isValid():
            if self.is_writeable:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.NoItemFlags

    def refresh_vertical_header(self):
        self.vertical_header_colors.clear()
        self.vertical_header_text.clear()
        for i in range(self.row_count):
            try:
                participant = self.protocol.messages[i].participant
                target = self.protocol.messages[i].target
            except IndexError:
                participant = None
                target = None

            participant_name = participant.shortname if participant else "?"
            target_name = target.shortname if target else "?"                
            self.vertical_header_text[i] = "{0} ({1} -> {2})".format(i + 1, participant_name, target_name)
