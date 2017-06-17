import os
import sys


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
    if output_view_type == 0:
        return "".join(map(str, map(int, bits)))
    elif output_view_type == 1:
        bits_str_list = list(map(str, map(int, bits)))

        if pad_zeros:
            bits_str_list += ["0"] * ((4 - (len(bits_str_list) % 4)) % 4)

        return "".join(map(lambda h: "{0:x}".format(h),
                           [int("".join(bits_str_list[i:i+4]), 2) for i in range(0, len(bits_str_list), 4)]))

    elif output_view_type == 2:
        bits_str_list = list(map(str, map(int, bits)))

        if pad_zeros:
            bits_str_list += ["0"] * ((8 - (len(bits_str_list) % 8)) % 8)

        return "".join(map(chr,
                           [int("".join(bits_str_list[i:i+8]), 2) for i in range(0, len(bits_str_list), 8)]))

    elif output_view_type == 3:
        return int("".join(map(str, map(int, bits))), 2)
