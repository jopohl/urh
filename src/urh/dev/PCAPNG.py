import os
import struct
import math

from urh.util.Logger import logger


# Refer to PCAPNG spec
# https://www.ietf.org/staging/draft-tuexen-opsawg-pcapng-02.html


def _build_pcapng_shb(shb_userappl: str = "", shb_hardware: str = "") -> bytes:
    BLOCKTYPE = 0x0A0D0D0A
    HEADERS_BLOCK_LENGTH = 28
    MAGIC_NUMBER = 0x1A2B3C4D
    VERSION_MAJOR, VERSION_MINOR = 1, 0
    SECTIONLENGTH = 0xFFFFFFFFFFFFFFFF  # -1 => Not specified

    shb_userappl_padded_len = math.ceil(len(shb_userappl) / 4) * 4
    shb_hardware_padded_len = math.ceil(len(shb_hardware) / 4) * 4

    total_block_len = HEADERS_BLOCK_LENGTH
    if shb_userappl_padded_len > 0:
        total_block_len += shb_userappl_padded_len + 4

    if shb_hardware_padded_len > 0:
        total_block_len += shb_hardware_padded_len + 4

    shb = struct.pack(
        ">IIIHHQ",
        BLOCKTYPE,
        total_block_len,
        MAGIC_NUMBER,
        VERSION_MAJOR,
        VERSION_MINOR,
        SECTIONLENGTH,
    )

    if shb_userappl != "":
        SHB_USERAPPL = 4
        strpad = shb_userappl.ljust(shb_userappl_padded_len, "\0")
        shb += struct.pack(">HH", SHB_USERAPPL, shb_userappl_padded_len)
        shb += bytes(strpad, "ascii")

    if shb_hardware != "":
        SHB_HARDWARE = 2
        strpad = shb_hardware.ljust(shb_hardware_padded_len, "\0")
        shb += struct.pack(">HH", SHB_HARDWARE, shb_hardware_padded_len)
        shb += bytes(strpad, "ascii")

    shb += struct.pack(">I", total_block_len)
    return shb


def _build_pcapng_idb(link_type) -> bytes:
    BLOCKTYPE = 0x00000001
    BLOCKLENGTH = 20
    SNAP_LEN = 0

    return struct.pack(
        ">IIHHII", BLOCKTYPE, BLOCKLENGTH, link_type, 0, SNAP_LEN, BLOCKLENGTH
    )


def _build_pcapng_epb(packet: bytes, timestamp: float) -> bytes:
    BLOCKTYPE = 0x00000006
    BLOCKHEADERLEN = 32
    INTERFACE_ID = 0

    captured_packet_len = len(packet)
    original_packet_len = captured_packet_len
    padded_packet_len = math.ceil(captured_packet_len / 4) * 4
    padding_len = padded_packet_len - original_packet_len
    padded_packet = packet + bytearray(padding_len)
    block_total_length = BLOCKHEADERLEN + padded_packet_len
    timestamp_int = int(timestamp * 1e6)  # Set the proper resolution
    timestamp_high = timestamp_int >> 32
    timestamp_low = timestamp_int & 0x00000000FFFFFFFF

    epb = struct.pack(
        ">IIIIIII",
        BLOCKTYPE,
        block_total_length,
        INTERFACE_ID,
        timestamp_high,
        timestamp_low,
        captured_packet_len,
        original_packet_len,
    )
    epb += padded_packet
    epb += struct.pack(">I", block_total_length)
    return epb


def create_pcapng_file(
    filename: str, shb_userappl: str = "", shb_hardware: str = "", link_type: int = 147
) -> bytes:
    if filename == "":
        return

    shb_bytes = _build_pcapng_shb(shb_userappl, shb_hardware)
    idb_bytes = _build_pcapng_idb(link_type)

    if os.path.isfile(filename):
        logger.warning("{0} already exists. Overwriting it".format(filename))

    with open(filename, "wb") as f:
        f.write(shb_bytes)
        f.write(idb_bytes)


def append_packets_to_pcapng(filename: str, packets: list, timestamps: list):
    with open(filename, "ab") as f:
        for packet, timestamp in zip(packets, timestamps):
            f.write(_build_pcapng_epb(packet, timestamp))
