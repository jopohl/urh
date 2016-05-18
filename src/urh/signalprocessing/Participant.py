import xml.etree.ElementTree as ET
import string
import random

class Participant(object):
    def __init__(self, name: str, shortname: str = None, address_hex: str = None, id: str = None):
        self.name = name if name else "unknown"
        self.shortname = shortname if shortname else name[0].upper() if len(name) > 0 else "X"
        self.address_hex = address_hex if address_hex else ""
        if id is None:
            self.__id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        else:
            self.__id = id

    def __repr__(self):
        return "Participant: {0} ({1}) addr: {2}".format(self.name, self.shortname, self.address_hex)

    def id_match(self, id):
        return self.__id == id

    def to_xml(self) -> ET.Element:
        root = ET.Element("participant")
        root.set("name", self.name)
        root.set("shortname", self.shortname)
        root.set("address_hex", self.address_hex)
        root.set("id", str(self.__id))

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        result = Participant("empty", id = tag.attrib["id"])
        result.name = tag.get("name", "Empty")
        result.shortname = tag.get("shortname", "X")
        result.address_hex = tag.get("address_hex", "")

        return result