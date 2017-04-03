import uuid
import xml.etree.cElementTree as ET
from enum import Enum
from xml.dom import minidom

from urh import constants


class FieldType(object):

    __slots__ = ["caption", "function", "display_format_index", "__id"]

    class Function(Enum):
        PREAMBLE = "preamble"
        SYNC = "synchronization"
        LENGTH = "length"
        SRC_ADDRESS = "source address"
        DST_ADDRESS = "destination address"
        SEQUENCE_NUMBER = "sequence number"
        CRC = "crc"
        CUSTOM = "custom"

    def __init__(self, caption: str, function: Function, display_format_index:int = None, id=None):
        self.caption = caption
        self.function = function

        if display_format_index is None:
            if self.function in (self.Function.PREAMBLE, self.Function.SYNC):
                self.display_format_index = 0
            elif self.function in (self.Function.DST_ADDRESS, self.Function.SRC_ADDRESS, self.Function.CRC):
                self.display_format_index = 1
            elif self.function in (self.Function.SEQUENCE_NUMBER, self.Function.LENGTH):
                self.display_format_index = 3
            else:
                self.display_format_index = 0
        else:
            self.display_format_index = display_format_index

        if id is None:
            self.__id = str(uuid.uuid4()) if id is None else id
        else:
            self.__id = id

    def __eq__(self, other):
        return isinstance(other, FieldType) and self.id_match(other.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "FieldType: {0} - {1} ({2})".format(self.function.name, self.caption, self.display_format_index)

    @property
    def id(self):
        return self.__id

    def id_match(self, id):
        return self.__id == id

    @staticmethod
    def default_field_types():
        """

        :rtype: list of FieldType
        """
        return [FieldType(function.value, function) for function in FieldType.Function]

    @staticmethod
    def load_from_xml():
        """

        :rtype: list of FieldType
        """

        e = ET.parse(constants.FIELD_TYPE_SETTINGS).getroot()

        result = []

        for tag in e.findall("field_type"):
            result.append(FieldType.from_xml(tag))

        return result

    def to_xml(self):
        return ET.Element("field_type", attrib={    "id": self.id,
                                                    "caption": self.caption,
                                                    "function": self.function.name,
                                                    "display_format_index": str(self.display_format_index)})
    @staticmethod
    def from_xml(tag):
        """

        :param tag: ET.Element
        :rtype: FieldType
        """
        caption = tag.get("caption", "")
        function = FieldType.Function[tag.get("function", "CUSTOM")]
        display_format_index = int(tag.get("display_format_index", -1))
        display_format_index = None if display_format_index == -1 else display_format_index

        id = tag.get("id", None)

        return FieldType(caption, function, display_format_index, id=id)


    @staticmethod
    def save_to_xml(field_types):
        """

        :type field_types: list of FieldType
        :return:
        """
        root = ET.Element("field_types")
        for field_type in field_types:
            root.append(field_type.to_xml())

        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(constants.FIELD_TYPE_SETTINGS, "w") as f:
            for line in xmlstr.split("\n"):
                if line.strip():
                    f.write(line + "\n")
