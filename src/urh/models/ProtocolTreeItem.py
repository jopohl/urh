import copy

from PyQt5.QtCore import Qt

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup


class ProtocolTreeItem(object):
    def __init__(self, data: ProtocolAnalyzer or ProtocolGroup, parent):
        """

        :param data: ProtocolGroup for Folder or ProtoAnalyzer for ProtoFrame
        :type parent: ProtocolTreeItem
        :return:
        """
        self.__itemData = data
        self.__parentItem = parent
        self.__childItems = data.items if type(data) == ProtocolGroup else []
        """:type: list of ProtocolTreeItem """

        self.copy_data = False  # For Writeable Mode in CFC
        self.__data_copy = None  # For Writeable Mode in CFC

    @property
    def protocol(self):
        if isinstance(self.__itemData, ProtocolAnalyzer):
            if self.copy_data:
                if self.__data_copy is None:
                    self.__data_copy = copy.deepcopy(self.__itemData)
                return self.__data_copy
            else:
                return self.__itemData
        else:
            return None

    @property
    def is_group(self):
        return type(self.__itemData) == ProtocolGroup

    @property
    def group(self):
        if type(self.__itemData) == ProtocolGroup:
            return self.__itemData
        else:
            return None

    @property
    def show(self):
        if self.is_group:
            return self.group_check_state
        else:
            return self.__itemData.show

    @show.setter
    def show(self, value: bool):
        value = Qt.Checked if value else Qt.Unchecked

        if not self.is_group:
            self.__itemData.show = value
            self.__itemData.qt_signals.show_state_changed.emit()
        else:
            for child in self.__childItems:
                child.__itemData.show = value
            if self.childCount() > 0:
                self.__childItems[0].__itemData.qt_signals.show_state_changed.emit()

    @property
    def group_check_state(self):
        if not self.is_group:
            return None

        if self.childCount() == 0:
            return Qt.Unchecked

        if all(child.show for child in self.children):
            return Qt.Checked
        elif any(child.show for child in self.children):
            return Qt.PartiallyChecked
        else:
            return Qt.Unchecked

    @property
    def children(self):
        return self.__childItems

    def parent(self):
        """
        :rtype: ProtocolTreeItem
        """
        return self.__parentItem

    def child(self, number):
        """
        :type number: int
        :rtype: ProtocolTreeItem
        """
        if number < self.childCount():
            return self.__childItems[number]
        else:
            return False

    def childCount(self) -> int:
        return len(self.__childItems)

    def indexInParent(self):
        if self.__parentItem is not None:
            return self.__parentItem.__childItems.index(self)

        return 0

    def columnCount(self) -> int:
        return 1

    def data(self):
        return self.__itemData.name

    def setData(self, value):
        self.__itemData.name = value
        return True

    def addGroup(self, name="New Group"):
        self.__childItems.append(ProtocolTreeItem(ProtocolGroup(name), self))

    def appendChild(self, child):
        child.setParent(self)
        self.__childItems.append(child)

    def addProtocol(self, proto):
        try:
            assert (isinstance(proto, ProtocolAnalyzer))
            self.__childItems.append(ProtocolTreeItem(proto, self))
        except AssertionError:
            return

    def insertChild(self, pos, child):
        self.__childItems.insert(pos, child)

    def removeAtIndex(self, index: int):
        child = self.__childItems[index]
        child.__parentItem = None
        self.__childItems.remove(child)

    def removeProtocol(self, protocol: ProtocolAnalyzer):
        assert self.is_group
        if protocol is None:
            return False

        for child in self.children:
            if child.protocol == protocol:
                child.setParent(None)
                return True
        return False

    def setParent(self, parent):
        if self.parent() is not None:
            self.parent().__childItems.remove(self)

        self.__parentItem = parent

    def index_of(self, child):
        return self.__childItems.index(child)

    def swapChildren(self, child1, child2):
        i1 = self.__childItems.index(child1)
        i2 = self.__childItems.index(child2)
        self.__childItems[i1], self.__childItems[i2] = self.__childItems[i2], self.__childItems[i1]

    def bringChildsToFront(self, childs):
        for child in childs:
            self.__childItems.insert(0, self.__childItems.pop(self.__childItems.index(child)))

    def bringChildsToIndex(self, index, childs):
        for child in reversed(childs):
            self.__childItems.insert(index, self.__childItems.pop(self.__childItems.index(child)))

    def containsChilds(self, childs):
        for child in childs:
            if child not in self.__childItems:
                return False
        return True

    def sortChilds(self):
        self.__childItems.sort()

    def __lt__(self, other):
        return self.data() < other.data()

    def clearChilds(self):
        self.__childItems[:] = []

    def __str__(self):
        return str(self.__itemData)
