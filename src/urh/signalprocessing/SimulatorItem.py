class SimulatorItem(object):
    def __init__(self):
        self.__parentItem = None
        self.__childItems = []

    def get_pos(self):
        if self.__parentItem is not None:
            return self.__parentItem.__childItems.index(self)

        return 0

    def insert_child(self, pos, child):
        self.__childItems.insert(pos, child)
        child.parent= self

    @property
    def parent(self):
        return self.__parentItem

    @parent.setter
    def parent(self, value):
        if self.parent is not None:
            self.parent.__childItems.remove(self)

        self.__parentItem = value

    @property
    def children(self):
        return self.__childItems

    def childCount(self) -> int:
        return len(self.__childItems)