import uuid
import xml.etree.ElementTree as ET


class Participant(object):

    __slots__ = ["name", "shortname", "address_hex", "color_index", "show", "relative_rssi", "__id"]

    def __init__(self, name: str, shortname: str = None, address_hex: str = None, color_index = 0, id: str = None, relative_rssi = 0):
        self.name = name if name else "unknown"
        self.shortname = shortname if shortname else name[0].upper() if len(name) > 0 else "X"
        self.address_hex = address_hex if address_hex else ""
        self.color_index = color_index
        self.show = True

        self.relative_rssi = relative_rssi

        if id is None:
            self.__id = str(uuid.uuid4()) if id is None else id
        else:
            self.__id = id

    def __eq__(self, other):
        return isinstance(other, Participant) and self.id_match(other.id)

    @property
    def id(self):
        return self.__id

    def __repr__(self):
        return "Participant: {0} ({1})".format(self.name, self.shortname)

    def id_match(self, id):
        return self.__id == id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        if isinstance(other, Participant):
            return self.shortname < other.shortname
        else:
            return False

    def to_xml(self) -> ET.Element:
        root = ET.Element("participant")
        root.set("name", self.name)
        root.set("shortname", self.shortname)
        root.set("address_hex", self.address_hex)
        root.set("color_index", str(self.color_index))
        root.set("id", str(self.__id))
        root.set("relative_rssi", str(self.relative_rssi))

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        name = tag.get("name", "Empty")
        shortname = tag.get("shortname", "X")
        address_hex = tag.get("address_hex", "")
        color_index = int(tag.get("color_index", 0))
        color_index = 0 if color_index < 0 else color_index
        relative_rssi = int(tag.get("relative_rssi", 0))
        return Participant(name, shortname=shortname, address_hex=address_hex, color_index=color_index, id = tag.attrib["id"], relative_rssi=relative_rssi)
