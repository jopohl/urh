import random
import string

import itertools
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, QModelIndex, Qt, QItemSelection

from urh import constants
from urh.signalprocessing.Participant import Participant


class ParticipantTableModel(QAbstractTableModel):
    INITIAL_NAMES = ["Alice", "Bob", "Carl", "Dave", "Eve", "Frank", "Grace", "Heidi", "Judy", "Mallory", "Oscar",
                     "Peggy", "Sybil", "Trudy", "Victor", "Walter"]

    updated = pyqtSignal()
    participant_edited = pyqtSignal()

    def __init__(self, participants):
        super().__init__()
        self.participants = participants
        self.header_labels = ["Name", "Shortname", "Color", "Relative RSSI", "Address (hex)"]

    def update(self):
        self.beginResetModel()
        self.endResetModel()
        self.updated.emit()

    def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.participants)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            part = self.participants[i]
            if j == 0:
                return part.name
            elif j == 1:
                return part.shortname
            elif j == 2:
                return part.color_index
            elif j == 3:
                return part.relative_rssi
            elif j == 4:
                return part.address_hex

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        i = index.row()
        j = index.column()
        if i >= len(self.participants):
            return False

        participant = self.participants[i]

        if j == 0:
            participant.name = value
        elif j == 1:
            participant.shortname = value
        elif j == 2:
            participant.color_index = int(value)
        elif j == 3:
            for other in self.participants:
                if other.relative_rssi == int(value):
                    other.relative_rssi = participant.relative_rssi
                    break
            participant.relative_rssi = int(value)
        elif j == 4:
            participant.address_hex = value

        self.update()
        self.participant_edited.emit()

        return True

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def __get_initial_name(self) -> (str, str):
        given_names = set(p.name for p in self.participants)
        name = next((name for name in self.INITIAL_NAMES if name not in given_names), None)
        if name is not None:
            return name, name[0]

        name = next(("P" + str(i) for i in itertools.count() if "P" + str(i) not in given_names), None)
        if name is not None:
            return name, name[1:]

        return "Participant X", "X"

    def add_participant(self):
        used_colors = set(p.color_index for p in self.participants)
        avail_colors = set(range(0, len(constants.PARTICIPANT_COLORS))) - used_colors
        if len(avail_colors) > 0:
            color_index = avail_colors.pop()
        else:
            color_index = random.choice(range(len(constants.PARTICIPANT_COLORS)))

        name, shortname = self.__get_initial_name()
        participant = Participant(name, shortname=shortname, color_index=color_index)
        self.participants.append(participant)
        participant.relative_rssi = len(self.participants) - 1

        self.update()
        self.participant_edited.emit()

    def remove_participants(self, selection: QItemSelection):
        if len(self.participants) < 1:
            return

        if selection.isEmpty():
            start, end = len(self.participants) - 1, len(self.participants) - 1  # delete last element
        else:
            start, end = min([rng.top() for rng in selection]), max([rng.bottom() for rng in selection])

        del self.participants[start:end + 1]
        num_removed = (end + 1) - start
        for participant in self.participants:
            if participant.relative_rssi > len(self.participants) - 1:
                participant.relative_rssi -= num_removed

        # fix duplicates
        n = len(self.participants)
        for p1, p2 in itertools.combinations(self.participants, 2):
            if p1.relative_rssi == p2.relative_rssi:
                p1.relative_rssi = next((i for i in range(n)
                                         if i not in set(p.relative_rssi for p in self.participants)),
                                        0)

        self.update()
        self.participant_edited.emit()

    def move_up(self, selection: QItemSelection):
        if selection.isEmpty() or len(self.participants) < 1:
            return None, None

        start, end = min([rng.top() for rng in selection]), max([rng.bottom() for rng in selection])
        if start == 0:
            return None, None

        for i in range(start, end + 1):
            self.participants[i], self.participants[i - 1] = self.participants[i - 1], self.participants[i]

        self.update()
        self.participant_edited.emit()

        return start, end

    def move_down(self, selection: QItemSelection):
        if selection.isEmpty() or len(self.participants) < 1:
            return None, None

        start, end = min([rng.top() for rng in selection]), max([rng.bottom() for rng in selection])
        if end >= len(self.participants) - 1:
            return None, None

        for i in reversed(range(start, end + 1)):
            self.participants[i], self.participants[i + 1] = self.participants[i + 1], self.participants[i]

        self.update()
        self.participant_edited.emit()

        return start, end
