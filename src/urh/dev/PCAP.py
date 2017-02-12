import os
import struct
import time

from urh.util.Logger import logger

from urh.signalprocessing.Message import Message


class PCAP(object):
    def __init__(self):
        self.timestamp_sec = None
        self.timestamp_nsec = None

    def reset_timestamp(self):
        self.timestamp_sec = None
        self.timestamp_nsec = None

    def build_global_header(self) -> bytes:
        MAGIC_NUMBER = 0xa1b23c4d # Nanosecond resolution
        VERSION_MAJOR, VERSION_MINOR = 2, 4
        THISZONE = 0
        SIGFIGS = 0
        SNAPLEN = 65535
        NETWORK = 147

        self.reset_timestamp()

        return struct.pack(">IHHiIII", MAGIC_NUMBER, VERSION_MAJOR, VERSION_MINOR, THISZONE, SIGFIGS, SNAPLEN, NETWORK)

    def build_packet(self, ts_sec: int, ts_nsec: int, data: bytes) -> bytes:
        if self.timestamp_nsec is None or self.timestamp_sec is None:
            self.timestamp_sec, self.timestamp_nsec = self.get_seconds_nseconds(time.time())

        self.timestamp_sec += int(ts_sec)
        self.timestamp_nsec += int(ts_nsec)
        if self.timestamp_nsec >= 1e9:
            self.timestamp_sec += int(self.timestamp_nsec / 1e9)
            self.timestamp_nsec = int(self.timestamp_nsec % 1e9)

        l = len(data)
        return struct.pack(">IIII", self.timestamp_sec, self.timestamp_nsec, l, l) + data

    def write_packets(self, packets, filename: str, sample_rate: int):
        """

        :type packets: list of Message
        :param filename:
        :return:
        """
        if os.path.isfile(filename):
            logger.warning("{0} already exists. Overwriting it".format(filename))

        with open(filename, "wb") as f:
            f.write(self.build_global_header())

        with open(filename, "ab") as f:
            rel_time_offset_ns = 0
            for pkt in packets:
                f.write(self.build_packet(0, rel_time_offset_ns, pkt.decoded_bits_buffer))
                rel_time_offset_ns = pkt.get_duration(sample_rate) * 10 ** 9

    @staticmethod
    def get_seconds_nseconds(timestamp):
        seconds = int(timestamp)
        nseconds = int((timestamp - seconds) * 10 ** 9)
        return seconds, nseconds
