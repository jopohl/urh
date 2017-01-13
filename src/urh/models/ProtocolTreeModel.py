from PyQt5.QtCore import QAbstractItemModel, pyqtSignal, QModelIndex, Qt, QMimeData
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMessageBox, QWidget

from urh import constants
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup


class ProtocolTreeModel(QAbstractItemModel):
    item_dropped = pyqtSignal()
    labels_on_group_dropped = pyqtSignal(list, int)
    group_deleted = pyqtSignal(int, int)
    proto_to_group_added = pyqtSignal(int)
    group_added = pyqtSignal(QModelIndex)


    def __init__(self, controller, parent=None):
        self.rootItem = ProtocolTreeItem(None, None)
        self.rootItem.addGroup()

        self.reference_protocol = -1
        self.controller = controller

        super().__init__(parent)

    @property
    def protocols(self):
        """
        :rtype: dict[int, list of ProtocolAnalyzer]
        """
        result = {}
        for i, group in enumerate(self.rootItem.children):
            result[i] = [child.protocol for child in group.children]

        return result

    def group_at(self, index: int) -> ProtocolGroup:
        return self.rootItem.child(index).group

    @property
    def ngroups(self):
        return self.rootItem.childCount()

    @property
    def groups(self):
        """

        :rtype: list of ProtocolGroup
        """
        return [self.group_at(i) for i in range(self.ngroups)]

    @property
    def protocol_tree_items(self):
        """
        :rtype: dict[int, list of ProtocolTreeItem]
        """
        result = {}
        for i, group in enumerate(self.rootItem.children):
            result[i] = [child for child in group.children]

        return result

    def get_groupid_for_index(self, index: QModelIndex) -> int:
        item = self.getItem(index)
        if item.parent() == self.rootItem:
            return self.rootItem.index_of(item)
        elif item == self.rootItem:
            return self.ngroups - 1 # Last group when dropped on root
        else:
            return self.rootItem.index_of(item.parent()) # Item is Protocol


    def getItem(self, index: QModelIndex) -> ProtocolTreeItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        parentItem = self.getItem(QModelIndex_parent)
        return parentItem.childCount()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def index(self, row: int, column: int, parent=None, *args, **kwargs):
        if parent is None:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex=None):
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        try:
            parentItem = childItem.parent()
        except AttributeError:
            return QModelIndex()

        if parentItem == self.rootItem or parentItem is None:
            return QModelIndex()

        return self.createIndex(parentItem.indexInParent(), 0, parentItem)

    def data(self, index: QModelIndex, role=None):
        item = self.getItem(index)
        if role == Qt.DisplayRole:
            return item.data()
        elif role == Qt.DecorationRole and item.is_group:
            return QIcon.fromTheme("folder")
        elif role == Qt.CheckStateRole:
            return item.show
        elif role == Qt.FontRole:
            if item.is_group and self.rootItem.index_of(item) in self.controller.active_group_ids:
                font = QFont()
                font.setBold(True)
                return font
            elif item.protocol in self.controller.selected_protocols:
                font = QFont()
                font.setBold(True)
                return font
        elif role == Qt.TextColorRole and item.protocol == self.reference_protocol:
            return constants.SELECTED_ROW_COLOR
        elif role == Qt.ToolTipRole:
            return item.data()

    def setData(self, index: QModelIndex, value, role=None):
        item = self.getItem(index)

        if role == Qt.EditRole and len(value) > 0:
            item.setData(value)
            return True
        elif role == Qt.CheckStateRole:
            item.show = value
            return True

        return False

    def add_protocol(self, protocol: ProtocolAnalyzer, group_id=0):
        if group_id >= self.ngroups:
            group_id = 0
        self.beginResetModel()
        self.rootItem.child(group_id).addProtocol(protocol)
        self.endResetModel()
        self.layoutChanged.emit()
        self.proto_to_group_added.emit(group_id)
        return self.groups[group_id]

    def remove_protocol(self, protocol: ProtocolAnalyzer):
        self.beginResetModel()
        result = False
        for group in self.rootItem.children:
            if group.removeProtocol(protocol):
                result = True
                break
        self.endResetModel()
        self.layoutChanged.emit()
        return result

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsDropEnabled
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled


    def supportedDragActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def mimeTypes(self):
        return['text/plain', 'text/uri-list']

    def mimeData(self, indexes):
        data = ''
        for index in indexes:
            parent_item = self.getItem(index.parent())
            if parent_item == self.rootItem:
                data += "{0},{1},{2}/".format(index.row(), index.column(), -1)
            else:
                data += "{0},{1},{2}/".format(index.row(), index.column(), self.rootItem.index_of(parent_item))
        mimeData = QMimeData()
        mimeData.setText(data)
        return mimeData

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if action == Qt.IgnoreAction:
            return True

        data_str = str(mimedata.text())
        if data_str.startswith("PLabels"):
            # Labels Dropped
            data_str = data_str.replace("'", "")
            label_ids = list(map(int, data_str.replace("PLabels:", "").split("/")))
            dropNode = self.getItem(parentIndex)
            if dropNode == self.rootItem:
                return False
            elif dropNode.is_group:
                parent = dropNode
            else:
                parent = dropNode.parent()

            dropped_group_id = self.rootItem.index_of(parent)

            self.labels_on_group_dropped.emit(label_ids, dropped_group_id)

            return True

        indexes = list(reversed(data_str.split("/")[:-1]))
        dragNodes = []

        # Ensure we only drop groups or files
        contains_groups = False
        contains_files = False

        for index in indexes:
            row, column, parent = map(int, index.split(","))
            if parent == -1:
                parent = self.rootItem
            else:
                parent = self.rootItem.child(parent)
            node = parent.child(row)
            if node.is_group:
                contains_groups = True
            else:
                contains_files = True

            if contains_files and contains_groups:
                QMessageBox.information(QWidget(), self.tr("Drag not supported"),
                           self.tr("You can only drag/drop groups or protocols, no mixtures of both."))
                return False

            dragNodes.append(node)

        dropNode = self.getItem(parentIndex)

        if dropNode == self.rootItem:
            # Append to Last Group when dropped on root
            try:
                dropNode = self.rootItem.children[-1]
            except IndexError:
                return False

        if not dropNode.is_group:
            parentNode = dropNode.parent()
            dropped_on_group = False
        else:
            parentNode = dropNode
            dropped_on_group = True

        if parentNode is None:
            return False

        if dropped_on_group and contains_groups:
            parentNode = dropNode.parent()
            pos = parentNode.index_of(dropNode)
            parentNode.bringChildsToIndex(pos, dragNodes)
        elif dropped_on_group:
            if parentNode.containsChilds(dragNodes):
                # "Nodes on parent folder Dropped"
                parentNode.bringChildsToFront(dragNodes)
            else:
                # "Nodes on distinct folder dropped"
                for dragNode in dragNodes:
                    parentNode.appendChild(dragNode)

                self.proto_to_group_added.emit(self.rootItem.index_of(parentNode))
        else:
            # Dropped on file
            if contains_groups:
                # Cant drop groups on files
                return False

            elif parentNode.containsChilds(dragNodes) and dropNode in parentNode.children:
                # "Nodes on node in parent folder dropped"
                pos = parentNode.index_of(dropNode)
                parentNode.bringChildsToIndex(pos, dragNodes)
            elif parentNode.containsChilds(dragNodes):
                parentNode.bringChildsToFront(dragNodes)
            else:
                # "Nodes on node in distinct folder dropped"
                pos = parentNode.index_of(dropNode)
                for dragNode in dragNodes:
                    dragNode.setParent(parentNode)
                    parentNode.insertChild(pos, dragNode)
                self.proto_to_group_added.emit(self.rootItem.index_of(parentNode))

        self.item_dropped.emit()
        return True

    def insertRow(self, row, parent=None, *args, **kwargs):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def removeRow(self, row, parentIndex=None, *args, **kwargs):
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex=None, *args, **kwargs):
        self.beginRemoveRows(parentIndex, row, row)
        node = self.getItem(parentIndex)
        node.removeAtIndex(row)
        self.endRemoveRows()

        return True

    def addGroup(self, name="New group"):
        self.rootItem.addGroup(name)
        child_nr = self.rootItem.childCount() - 1
        self.group_added.emit(self.createIndex(child_nr, 0, self.rootItem.child(child_nr)))

    def deleteGroup(self, group_item: ProtocolTreeItem):
        if self.rootItem.childCount() == 1:
            QMessageBox.critical(self.controller, self.tr("Group not deletable"),
                           self.tr("You can't delete the last group. Think about the children, they would be homeless!"))
            return

        group_id = self.rootItem.index_of(group_item)
        if group_id == 0:
            new_group_index = 1
        else:
            new_group_index = group_id - 1

        new_group = self.rootItem.children[new_group_index]

        for i in reversed(range(group_item.childCount())):
            new_group.appendChild(group_item.children[i])

        self.removeRow(group_id, QModelIndex())
        self.group_deleted.emit(group_id, new_group_index)

    def moveToGroup(self, items, new_group_id: int):
        """
        :type items: list of ProtocolTreeItem
        """
        group = self.rootItem.child(new_group_id)
        for item in items:
            group.appendChild(item)
        self.controller.refresh()

    def sort_group(self, sortgroup_id):
        self.blockSignals(True)
        self.rootItem.child(sortgroup_id).sortChilds()
        self.controller.refresh()
        self.blockSignals(False)

    def set_copy_mode(self, use_copy: bool):
        """
        Set all protocols in copy mode. They will return a copy of their protocol.
        This is used for writable mode in CFC.

        :param use_copy:
        :return:
        """
        for group in self.rootItem.children:
            for proto in group.children:
                proto.copy_data = use_copy
