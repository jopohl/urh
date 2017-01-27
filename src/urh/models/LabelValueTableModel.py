from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class LabelValueTableModel(QAbstractTableModel):
    header_labels = ["Name", 'Display format', 'Value']

    def __init__(self, proto_analyzer: ProtocolAnalyzer, controller, parent=None):
        super().__init__(parent)
        self.proto_analyzer = proto_analyzer
        self.controller = controller
        self.__message_index = 0
        self.display_labels = controller.active_message_type
        """:type: urh.signalprocessing.MessageType.MessageType"""

        self.bit_str = self.proto_analyzer.decoded_proto_bits_str
        self.hex_str = self.proto_analyzer.decoded_hex_str
        self.ascii_str = self.proto_analyzer.decoded_ascii_str

    @property
    def message_index(self):
        return self.__message_index

    @message_index.setter
    def message_index(self, value):
        self.__message_index = value
        self.update()

    @property
    def message(self):
        if self.message_index != -1 and self.message_index < len(self.proto_analyzer.messages):
            return self.proto_analyzer.messages[self.message_index]
        else:
            return None

    def update(self):
        self.display_labels = self.controller.active_message_type
        self.bit_str = self.proto_analyzer.decoded_proto_bits_str
        self.hex_str = self.proto_analyzer.decoded_hex_str
        self.ascii_str = self.proto_analyzer.decoded_ascii_str
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.display_labels)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            lbl = self.display_labels[i]
            if not lbl:
                return None

            if j == 0:
                return lbl.name
            elif j == 1:
                return lbl.DISPLAY_FORMATS[lbl.display_format_index]
            elif j == 2:
                if not self.message:
                    return None
                start, end = self.message.get_label_range(lbl, lbl.display_format_index % 3, True)
                if lbl.display_format_index == 0:
                    try:
                        return self.bit_str[self.message_index][start:end]
                    except IndexError:
                        return None
                elif lbl.display_format_index == 1:
                    try:
                        return self.hex_str[self.message_index][start:end]
                    except IndexError:
                        return None
                elif lbl.display_format_index == 2:
                    try:
                        return self.ascii_str[self.message_index][start:end]
                    except IndexError:
                        return None
                elif lbl.display_format_index == 3:
                    try:
                        try:
                            decimal = int(self.bit_str[self.message_index][start:end], 2)
                        except IndexError:
                            return None
                    except ValueError:
                        decimal = ""
                    return decimal

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            lbl = self.display_labels[index.row()]
            if index.column() == 1:
                lbl.display_format_index = value

    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        if index.column() == 1:
            flags |= Qt.ItemIsEditable

        return flags
