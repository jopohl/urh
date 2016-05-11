import unittest

from urh.dev.PCAP import PCAP


class TestPCAP(unittest.TestCase):
    def test_write(self):
        pcap = PCAP()
        packet1 = b"\x01\x02\x03"
        packet2 = b"\x02\x03\x04"

        print(pcap.build_global_header())
        print(pcap.build_packet(10, 22, packet1, first=True))
        print(pcap.build_packet(0, 22e9+42, packet2))