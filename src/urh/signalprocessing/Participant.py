import xml.etree.ElementTree as ET


class Participant(object):
    def __init__(self, name: str, shortname: str = None, address_hex: str = None):
        self.name = name if name else "unknown"
        self.shortname = shortname if shortname else name[0].upper() if len(name) > 0 else "X"
        self.address_hex = address_hex if address_hex else ""

    def __repr__(self):
        return "Participant: {0} ({1}) addr: {2}".format(self.name, self.shortname, self.address_hex)

    def to_xml(self) -> ET.Element:
        root = ET.Element("participant")
        for attr, val in vars(self).items():
            root.set(attr, str(val))
        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        result = Participant("empty")
        for attrib, value in tag.attrib.items():
            setattr(result, attrib, value)
        return result