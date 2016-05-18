import xml.etree.ElementTree as ET
import string
import random

from PyQt5.QtCore import QObject, pyqtSignal


class Participant(QObject):
    name_changed = pyqtSignal(str)
    shortname_changed = pyqtSignal(str)
    address_hex_changed = pyqtSignal(str)
    color_index_changed = pyqtSignal(int)

    def __init__(self, name: str, shortname: str = None, address_hex: str = None, color_index = 0, id: str = None):
        super().__init__()
        self.__name = name if name else "unknown"
        self.__shortname = shortname if shortname else name[0].upper() if len(name) > 0 else "X"
        self.__address_hex = address_hex if address_hex else ""
        self.__color_index = color_index

        if id is None:
            self.__id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        else:
            self.__id = id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if value != self.__name:
            self.__name = value
            self.name_changed.emit(self.__name)

    @property
    def shortname(self) -> str:
        return self.__shortname

    @shortname.setter
    def shortname(self, value: str):
        if value != self.__shortname:
            self.__shortname = value
            self.shortname_changed.emit(self.__shortname)

    @property
    def address_hex(self) -> str:
        return self.__address_hex

    @address_hex.setter
    def address_hex(self, value: str):
        if self.__address_hex != value:
            self.__address_hex = value
            self.address_hex_changed.emit(self.__address_hex)

    @property
    def color_index(self):
        return self.__color_index

    @color_index.setter
    def color_index(self, value):
        if value != self.__color_index:
            self.__color_index = value
            self.color_index_changed.emit(self.__color_index)


    def __repr__(self):
        return "Participant: {0} ({1}) addr: {2}".format(self.name, self.shortname, self.address_hex)

    def id_match(self, id):
        return self.__id == id

    def to_xml(self) -> ET.Element:
        root = ET.Element("participant")
        root.set("name", self.name)
        root.set("shortname", self.shortname)
        root.set("address_hex", self.address_hex)
        root.set("color_index", str(self.color_index))
        root.set("id", str(self.__id))

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        name = tag.get("name", "Empty")
        shortname = tag.get("shortname", "X")
        address_hex = tag.get("address_hex", "")
        color_index = int(tag.get("color_index", 0))
        return Participant(name, shortname=shortname, address_hex=address_hex, color_index=color_index, id = tag.attrib["id"])