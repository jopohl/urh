import array
import copy
from enum import Enum
from xml.etree import ElementTree as ET

from urh.util import util
from urh.util.GenericCRC import GenericCRC


class WSPChecksum(object):
    """
    This class implements the three checksums from Wireless Short Packet (WSP) standard
    http://hes-standards.org/doc/SC25_WG1_N1493.pdf
    """

    class ChecksumMode(Enum):
        auto = 0
        checksum4 = 1
        checksum8 = 2
        crc8 = 3

    CRC_8_POLYNOMIAL = array.array("B", [1,
                                         0, 0, 0, 0, 0, 1, 1, 1])  # x^8+x^2+x+1

    def __init__(self, mode=ChecksumMode.auto):
        self.mode = mode
        self.caption = str(mode)

    def __eq__(self, other):
        if not isinstance(other, WSPChecksum):
            return False

        return self.mode == other.mode

    def __hash__(self):
        return hash(self.mode)

    def calculate(self, msg: array.array) -> array.array:
        """
        Get the checksum for a WSP message. There are three hashes possible:
        1) 4 Bit Checksum - For Switch Telegram (RORG=5 or 6 and STATUS = 0x20 or 0x30)
        2) 8 Bit Checksum: STATUS bit 2^7 = 0
        3) 8 Bit CRC: STATUS bit 2^7 = 1

        :param msg: the message without Preamble/SOF and EOF. Message starts with RORG and ends with CRC
        """
        try:
            if self.mode == self.ChecksumMode.auto:
                if msg[0:4] == util.hex2bit("5") or msg[0:4] == util.hex2bit("6"):
                    # Switch telegram
                    return self.checksum4(msg)

                status = msg[-16:-8]
                if status[0]:
                    return self.crc8(msg[:-8])  # ignore trailing hash
                else:
                    return self.checksum8(msg[:-8])  # ignore trailing hash

            elif self.mode == self.ChecksumMode.checksum4:
                return self.checksum4(msg)
            elif self.mode == self.ChecksumMode.checksum8:
                return self.checksum8(msg[:-8])
            elif self.mode == self.ChecksumMode.crc8:
                return self.crc8(msg[:-8])

        except IndexError:
            return None

    @classmethod
    def search_for_wsp_checksum(cls, bits_behind_sync):
        data_start, data_stop, crc_start, crc_stop = 0, 0, 0, 0

        if bits_behind_sync[-4:].tobytes() != array.array("B", [1, 0, 1, 1]).tobytes():
            return 0, 0, 0, 0  # Check for EOF

        rorg = bits_behind_sync[0:4].tobytes()
        if rorg == array.array("B", [0, 1, 0, 1]).tobytes() or rorg == array.array("B", [0, 1, 1, 0]).tobytes():
            # Switch telegram
            if cls.checksum4(bits_behind_sync[-8:]).tobytes() == bits_behind_sync[-8:-4].tobytes():
                crc_start = len(bits_behind_sync) - 8
                crc_stop = len(bits_behind_sync) - 4
                data_stop = crc_start
                return data_start, data_stop, crc_start, crc_stop

        # todo: Find crc8 and checksum8

        return 0, 0, 0, 0

    @classmethod
    def checksum4(cls, bits: array.array) -> array.array:
        hash = 0
        val = copy.copy(bits)
        val[-4:] = array.array("B", [False, False, False, False])
        for i in range(0, len(val), 8):
            hash += int("".join(map(str, map(int, val[i:i + 8]))), 2)
        hash = (((hash & 0xf0) >> 4) + (hash & 0x0f)) & 0x0f
        return array.array("B", list(map(bool, map(int, "{0:04b}".format(hash)))))

    @classmethod
    def checksum8(cls, bits: array.array) -> array.array:
        hash = 0
        for i in range(0, len(bits) - 8, 8):
            hash += int("".join(map(str, map(int, bits[i:i + 8]))), 2)
        return array.array("B", list(map(bool, map(int, "{0:08b}".format(hash % 256)))))

    @classmethod
    def crc8(cls, bits: array.array):
        return array.array("B", GenericCRC(polynomial=cls.CRC_8_POLYNOMIAL).crc(bits))

    def to_xml(self) -> ET.Element:
        root = ET.Element("wsp_checksum")
        root.set("mode", str(self.mode.name))
        return root

    @classmethod
    def from_xml(cls, tag: ET.Element):
        return WSPChecksum(mode=WSPChecksum.ChecksumMode[tag.get("mode", "auto")])
