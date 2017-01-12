from urh.signalprocessing.FieldType import FieldType

class SimulatorProtocolLabel(object):

    def __init__(self, name: str, value: str, length: int, color_index: int, type=None):
        self.__name = name
        self.value = value
        self.length = length
        self.color_index = color_index
        self.__type = type

    @property
    def name(self):
        if not self.__name:
            self.__name = "No name"

        return self.__name

    @name.setter
    def name(self, val):
        if val:
            self.__name = val

    @property
    def type(self) -> FieldType:
        return self.__type

    @type.setter
    def type(self, value: FieldType):
        if value != self.type:
            self.__type = value