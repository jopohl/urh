import array
import os
import shlex
import sys
import time
from xml.dom import minidom
from xml.etree import ElementTree as ET

import shutil
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QTableWidgetItem

from urh import constants
from urh.util.Logger import logger

DEFAULT_PROGRAMS_WINDOWS = {}

def profile(func):
    def func_wrapper(*args):
        t = time.perf_counter()
        result = func(*args)
        print("{} took {:.2f}ms".format(func, 1000 * (time.perf_counter() - t)))
        return result

    return func_wrapper


def set_icon_theme():
    if sys.platform != "linux" or constants.SETTINGS.value("icon_theme_index", 0, int) == 0:
        # noinspection PyUnresolvedReferences
        import urh.ui.xtra_icons_rc
        QIcon.setThemeName("oxy")
    else:
        QIcon.setThemeName("")


def set_windows_lib_path():
    dll_dir = get_windows_lib_path()
    if dll_dir:
        os.environ['PATH'] = dll_dir + ";" + os.environ['PATH']


def get_windows_lib_path():
    dll_dir = ""
    if sys.platform == "win32":
        if not hasattr(sys, "frozen"):
            util_dir = os.path.dirname(os.path.realpath(__file__)) if not os.path.islink(__file__) \
                else os.path.dirname(os.path.realpath(os.readlink(__file__)))
            urh_dir = os.path.realpath(os.path.join(util_dir, ".."))
            assert os.path.isdir(urh_dir)

            arch = "x64" if sys.maxsize > 2 ** 32 else "x86"
            dll_dir = os.path.realpath(os.path.join(urh_dir, "dev", "native", "lib", "win", arch))
        else:
            dll_dir = os.path.dirname(sys.executable)

    return dll_dir


def convert_bits_to_string(bits, output_view_type: int, pad_zeros=False, lsb=False, lsd=False):
    """
    Convert bit array to string
    :param bits: Bit array
    :param output_view_type: Output view type index
    0 = bit, 1=hex, 2=ascii, 3=decimal 4=binary coded decimal (bcd)
    :param pad_zeros:
    :param lsb: Least Significant Bit   -> Reverse bits first
    :param lsd: Least Significant Digit -> Reverse result at end
    :return:
    """
    bits_str = "".join(["1" if b else "0" for b in bits])

    if output_view_type == 4:
        # For BCD we need to enforce padding
        pad_zeros = True

    if pad_zeros and output_view_type in (1, 2, 4):
        n = 4 if output_view_type in (1, 4) else 8 if output_view_type == 2 else 1
        bits_str += "0" * ((n - (len(bits_str) % n)) % n)

    if lsb:
        # Reverse bit string
        bits_str = bits_str[::-1]

    if output_view_type == 0:  # bt
        result = bits_str

    elif output_view_type == 1:  # hex
        result = "".join(["{0:x}".format(int(bits_str[i:i + 4], 2)) for i in range(0, len(bits_str), 4)])

    elif output_view_type == 2:  # ascii
        result = "".join(map(chr,
                             [int("".join(bits_str[i:i + 8]), 2) for i in range(0, len(bits_str), 8)]))

    elif output_view_type == 3:  # decimal
        try:
            result = str(int(bits_str, 2))
        except ValueError:
            return None
    elif output_view_type == 4:  # bcd
        error_symbol = "?"
        lut = {"{0:04b}".format(i): str(i) if i < 10 else error_symbol for i in range(16)}
        result = "".join([lut[bits_str[i:i + 4]] for i in range(0, len(bits_str), 4)])
    else:
        raise ValueError("Unknown view type")

    if lsd:
        # reverse result
        return result[::-1]
    else:
        return result


def hex2bit(hex_str: str) -> array.array:
    if not isinstance(hex_str, str):
        return array.array("B", [])

    if hex_str[:2] == "0x":
        hex_str = hex_str[2:]

    try:
        bitstring = "".join("{0:04b}".format(int(h, 16)) for h in hex_str)
        return array.array("B", [True if x == "1" else False for x in bitstring])
    except (TypeError, ValueError) as e:
        logger.error(str(e))
        result = array.array("B", [])

    return result


def create_textbox_dialog(content: str, title: str, parent) -> QDialog:
    d = QDialog(parent)
    d.resize(800, 600)
    d.setWindowTitle(title)
    layout = QVBoxLayout(d)
    text_edit = QPlainTextEdit(content)
    text_edit.setReadOnly(True)
    layout.addWidget(text_edit)
    d.setLayout(layout)
    return d


def string2bits(bit_str: str) -> array.array:
    return array.array("B", map(int, bit_str))


def bit2hex(bits: array.array, pad_zeros=False) -> str:
    return convert_bits_to_string(bits, 1, pad_zeros)


def aggregate_bits(bits: array.array, size=4) -> array.array:
    result = array.array("B", [])

    for i in range(0, len(bits), size):
        h = 0
        for k in range(size):
            try:
                h += (2 ** (size - 1 - k)) * bits[i + k]
            except IndexError:
                # Implicit padding with zeros
                continue
        result.append(h)

    return result


def clip(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def file_can_be_opened(filename: str):
    try:
        open(filename, "r").close()
        return True
    except Exception as e:
        if not isinstance(e, FileNotFoundError):
            logger.debug(str(e))
        return False


def create_table_item(content):
    item = QTableWidgetItem(str(content))
    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    return item


def write_xml_to_file(xml_tag: ET.Element, filename: str):
    xml_str = minidom.parseString(ET.tostring(xml_tag)).toprettyxml(indent="  ")
    with open(filename, "w") as f:
        for line in xml_str.split("\n"):
            if line.strip():
                f.write(line + "\n")


def get_monospace_font() -> QFont:
    fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    fixed_font.setPointSize(QApplication.instance().font().pointSize())
    return fixed_font


def get_name_from_filename(filename: str):
    if not isinstance(filename, str):
        return "No Name"

    return os.path.basename(filename).split(".")[0]


def get_default_windows_program_for_extension(extension: str):
    if os.name != "nt":
        return None

    if not extension.startswith("."):
        extension = "." + extension

    if extension in DEFAULT_PROGRAMS_WINDOWS:
        return DEFAULT_PROGRAMS_WINDOWS[extension]

    try:
        assoc = subprocess.check_output("assoc " + extension, shell=True, stderr=subprocess.PIPE).decode().split("=")[1]
        ftype = subprocess.check_output("ftype " + assoc, shell=True).decode().split("=")[1].split(" ")[0]
        ftype = ftype.replace('"', '')
        assert shutil.which(ftype) is not None
    except Exception:
        return None

    DEFAULT_PROGRAMS_WINDOWS[extension] = ftype
    return ftype


def parse_command(command: str):
    try:
        posix = os.name != "nt"
        splitted = shlex.split(command, posix=posix)
        # strip quotations
        if not posix:
            splitted = [s.replace('"', '').replace("'", "") for s in splitted]
    except ValueError:
        splitted = []   # e.g. when missing matching "

    if len(splitted) == 0:
        return "", []

    cmd = [splitted.pop(0)]

    # This is for legacy support, if you have filenames with spaces and did not quote them
    while shutil.which(" ".join(cmd)) is None and len(splitted) > 0:
        cmd.append(splitted.pop(0))

    return " ".join(cmd), splitted


def run_command(command, param: str=None, use_stdin=False, detailed_output=False):
    cmd, arg = parse_command(command)
    if shutil.which(cmd) is None:
        logger.error("Could not find {}".format(cmd))
        return ""

    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if "." in cmd:
            default_app = get_default_windows_program_for_extension(cmd.split(".")[-1])
            if default_app:
                arg.insert(0, cmd)
                cmd = default_app

    call_list = [cmd] + arg
    try:
        if detailed_output:
            if param is not None:
                call_list.append(param)

            p = subprocess.Popen(call_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            out, err = p.communicate()
            result = "{} exited with {}".format(" ".join(call_list), p.returncode)
            if out.decode():
                result += " stdout: {}".format(out.decode())
            if err.decode():
                result += " stderr: {}".format(err.decode())
            return result
        elif use_stdin:
            p = subprocess.Popen(call_list, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                 startupinfo=startupinfo)
            param = param.encode() if param is not None else None
            out, _ = p.communicate(param)
            return out.decode()
        else:
            if param is not None:
                call_list.append(param)

            return subprocess.check_output(call_list, stderr=subprocess.PIPE, startupinfo=startupinfo).decode()
    except Exception as e:
        msg = "Could not run {} ({})".format(cmd, e)
        logger.error(msg)
        if detailed_output:
            return msg
        else:
            return ""


def validate_command(command: str):
    if not isinstance(command, str):
        return False

    cmd, _ = parse_command(command)
    return shutil.which(cmd) is not None
