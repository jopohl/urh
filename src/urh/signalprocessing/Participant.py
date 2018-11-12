import uuid
import xml.etree.ElementTree as ET


class Participant(object):
    __slots__ = ["name", "shortname", "address_hex", "color_index", "show", "simulate", "relative_rssi", "__id"]

    def __init__(self, name: str, shortname: str = None, address_hex: str = None,
                 color_index=0, id: str = None, relative_rssi=0, simulate=False):
        self.name = name if name else "unknown"
        self.shortname = shortname if shortname else name[0].upper() if len(name) > 0 else "X"
        self.address_hex = address_hex if address_hex else ""
        self.color_index = color_index
        self.show = True
        self.simulate = simulate

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
        if self.address_hex:
            return "{0} ({1}) [{2}]".format(self.name, self.shortname, self.address_hex)
        else:
            return "{0} ({1})".format(self.name, self.shortname)

    def __str__(self):
        return repr(self)

    def id_match(self, id):
        return self.__id == id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        if isinstance(other, Participant):
            return self.shortname < other.shortname
        else:
            return False

    @staticmethod
    def find_matching(participant_id: str, participants: list):
        return next((p for p in participants if p.id_match(participant_id)), None)

    def to_xml(self) -> ET.Element:
        root = ET.Element("participant")
        root.set("name", self.name)
        root.set("shortname", self.shortname)
        root.set("address_hex", self.address_hex)
        root.set("color_index", str(self.color_index))
        root.set("id", str(self.__id))
        root.set("relative_rssi", str(self.relative_rssi))
        root.set("simulate", str(int(bool(self.simulate))))

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        name = tag.get("name", "Empty")
        shortname = tag.get("shortname", "X")
        address_hex = tag.get("address_hex", "")
        color_index = int(tag.get("color_index", 0))
        color_index = 0 if color_index < 0 else color_index
        relative_rssi = int(tag.get("relative_rssi", 0))
        try:
            simulate = bool(int(tag.get("simulate", "0")))
        except ValueError:
            simulate = False

        return Participant(name, shortname=shortname, address_hex=address_hex, color_index=color_index,
                           id=tag.attrib["id"], relative_rssi=relative_rssi, simulate=simulate)

    @staticmethod
    def participants_to_xml_tag(participants: list) -> ET.Element:
        participants_tag = ET.Element("participants")
        for participant in participants:
            participants_tag.append(participant.to_xml())
        return participants_tag

    @staticmethod
    def read_participants_from_xml_tag(xml_tag: ET.Element):
        if xml_tag is None:
            return []

        if xml_tag.tag != "participants":
            xml_tag = xml_tag.find("participants")

        if xml_tag is None:
            return []

        participants = []
        for parti_tag in xml_tag.findall("participant"):
            participants.append(Participant.from_xml(parti_tag))
        return participants
