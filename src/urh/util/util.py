import os
import sys

import array

from urh.util.Logger import logger


def set_windows_lib_path():
    if sys.platform == "win32":
        util_dir = os.path.dirname(os.path.realpath(__file__)) if not os.path.islink(__file__) \
            else os.path.dirname(os.path.realpath(os.readlink(__file__)))
        urh_dir = os.path.realpath(os.path.join(util_dir, ".."))
        assert os.path.isdir(urh_dir)

        arch = "x64" if sys.maxsize > 2**32 else "x86"
        dll_dir = os.path.realpath(os.path.join(urh_dir, "dev", "native", "lib", "win", arch))
        print("Using DLLs from:", dll_dir)
        os.environ['PATH'] = os.environ['PATH'] + ";" + dll_dir


def convert_bits_to_string(bits, output_view_type: int, pad_zeros=False):
    bits_str = "".join(["1" if b else "0" for b in bits])

    if output_view_type == 0:
        return bits_str

    elif output_view_type == 1:
        if pad_zeros:
            bits_str += "0" * ((4 - (len(bits_str) % 4)) % 4)

        return hex(int(bits_str, 2))[2:]

    elif output_view_type == 2:
        if pad_zeros:
            bits_str += ["0"] * ((8 - (len(bits_str) % 8)) % 8)

        return "".join(map(chr,
                           [int("".join(bits_str[i:i+8]), 2) for i in range(0, len(bits_str), 8)]))

    elif output_view_type == 3:
        return int(bits_str, 2)


def hex2bit(hex_str: str) -> array.array:
    if not isinstance(hex_str, str):
        return array.array("B", [])

    try:
        bitstring = bin(int(hex_str, base=16))[2:]
        if len(bitstring) % 4 != 0:
            bitstring = "0" * (4 - (len(bitstring) % 4)) + bitstring
        return array.array("B", [True if x == "1" else False for x in bitstring])
    except (TypeError, ValueError) as e:
        logger.error(str(e))
        result = array.array("B", [])

    return result


def bit2hex(bits: array.array, pad_zeros=False) -> str:
    return convert_bits_to_string(bits, 1, pad_zeros)
