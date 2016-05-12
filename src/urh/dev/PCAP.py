import os
import struct
import time
from urh.signalprocessing.ProtocolBlock import ProtocolBlock


class PCAP(object):
    def __init__(self):
        self.timestamp_sec = None
        self.timestamp_nsec = None

    def build_global_header(self) -> bytes:
        MAGIC_NUMBER = 0xa1b23c4d # Nanosecond resolution
        VERSION_MAJOR, VERSION_MINOR = 2, 4
        THISZONE = 0
        SIGFIGS = 0
        SNAPLEN = 65535
        NETWORK = 1337 # TODO Find a good type: https://wiki.wireshark.org/Development/LibpcapFileFormat

        return struct.pack(">IHHiIII", MAGIC_NUMBER, VERSION_MAJOR, VERSION_MINOR, THISZONE, SIGFIGS, SNAPLEN, NETWORK)

    def build_packet(self, ts_sec: int, ts_nsec: int, data: bytes, first=False) -> bytes:
        if first:
            self.timestamp_sec, self.timestamp_nsec = self.get_seconds_nseconds(time.time())

        self.timestamp_sec += ts_sec
        self.timestamp_nsec += ts_nsec
        if self.timestamp_nsec >= 1e9:
            self.timestamp_sec += int(self.timestamp_nsec / 1e9)
            self.timestamp_nsec = int(self.timestamp_nsec % 1e9)

        print(self.timestamp_sec, self.timestamp_nsec)

        l = len(data)
        return struct.pack(">IIII", self.timestamp_sec, self.timestamp_nsec, l, l) + data

    def write_packets(self, packets, filename: str):
        """

        :type packets: list of ProtocolBlock
        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            with open(filename, "wb") as f:
                f.write(self.build_global_header())

        #with open(filename, "ab") as f:
        #    for pkt in packets:
        #        pkt.absolute_time





    @staticmethod
    def get_seconds_nseconds(timestamp):
        seconds = int(timestamp)
        nseconds = int((timestamp - seconds) * 10 ** 9)
        return seconds, nseconds