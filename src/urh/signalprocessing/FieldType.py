import xml.etree.ElementTree as ET
from enum import Enum
from xml.dom import minidom

from urh import settings


class FieldType(object):
    __slots__ = ["caption", "function", "display_format_index"]

    class Function(Enum):
        PREAMBLE = "preamble"
        SYNC = "synchronization"
        LENGTH = "length"
        SRC_ADDRESS = "source address"
        DST_ADDRESS = "destination address"
        SEQUENCE_NUMBER = "sequence number"
        TYPE = "type"
        DATA = "data"
        CHECKSUM = "checksum"
        CUSTOM = "custom"

    def __init__(
        self, caption: str, function: Function, display_format_index: int = None
    ):
        self.caption = caption
        self.function = function

        if display_format_index is None:
            if self.function in (self.Function.PREAMBLE, self.Function.SYNC):
                self.display_format_index = 0
            elif self.function in (
                self.Function.DST_ADDRESS,
                self.Function.SRC_ADDRESS,
                self.Function.CHECKSUM,
            ):
                self.display_format_index = 1
            elif self.function in (self.Function.SEQUENCE_NUMBER, self.Function.LENGTH):
                self.display_format_index = 3
            else:
                self.display_format_index = 0
        else:
            self.display_format_index = display_format_index

    def __eq__(self, other):
        return (
            isinstance(other, FieldType)
            and self.caption == other.caption
            and self.function == other.function
        )

    def __repr__(self):
        return "FieldType: {0} - {1} ({2})".format(
            self.function.name, self.caption, self.display_format_index
        )

    @staticmethod
    def from_caption(caption: str):
        try:
            ft_function = FieldType.Function(caption)
        except ValueError:
            return None
        return FieldType(caption, ft_function)

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

        e = ET.parse(settings.FIELD_TYPE_SETTINGS).getroot()

        result = []

        for tag in e.findall("field_type"):
            result.append(FieldType.from_xml(tag))

        return result

    def to_xml(self):
        return ET.Element(
            "field_type",
            attrib={
                "caption": self.caption,
                "function": self.function.name,
                "display_format_index": str(self.display_format_index),
            },
        )

    @staticmethod
    def from_xml(tag):
        """

        :param tag: ET.Element
        :rtype: FieldType
        """
        caption = tag.get("caption", "")
        function_str = tag.get("function", "CUSTOM")
        if function_str == "CRC":
            function_str = "CHECKSUM"  # legacy

        try:
            function = FieldType.Function[function_str]
        except KeyError:
            function = FieldType.Function.CUSTOM

        display_format_index = int(tag.get("display_format_index", -1))
        display_format_index = (
            None if display_format_index == -1 else display_format_index
        )

        return FieldType(caption, function, display_format_index)

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
        with open(settings.FIELD_TYPE_SETTINGS, "w") as f:
            for line in xmlstr.split("\n"):
                if line.strip():
                    f.write(line + "\n")
