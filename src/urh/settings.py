# QT5 = True
import os
import sys

import psutil
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor

from urh.util.Formatter import Formatter
from urh.util.Logger import logger


global __qt_settings


def __get_qt_settings():
    global __qt_settings

    try:
        __qt_settings.fileName()
    except:
        __qt_settings = QSettings(
            QSettings.IniFormat, QSettings.UserScope, "urh", "urh"
        )

    return __qt_settings


def get_qt_settings_filename():
    return __get_qt_settings().fileName()


MAX_RECENT_FILE_NR = 10
ZOOM_TICKS = 10

PIXELS_PER_PATH = 5000

SPECTRUM_BUFFER_SIZE = 2**15
SNIFF_BUFFER_SIZE = 5 * 10**7
CONTINUOUS_BUFFER_SIZE_MB = 50

PAUSE_TRESHOLD = 10
RECT_BIT_WIDTH = 10
BIT_SCENE_HEIGHT = 100

TRANSPARENT_COLOR = QColor(Qt.transparent)

LINECOLOR = QColor.fromRgb(225, 225, 225)
LINECOLOR_I = QColor.fromRgb(50, 50, 225)
LINECOLOR_Q = QColor.fromRgb(55, 53, 53)
BGCOLOR = QColor.fromRgb(55, 53, 53)
AXISCOLOR = QColor.fromRgb(200, 200, 200, 100)
ARROWCOLOR = QColor.fromRgb(204, 120, 50)

ERROR_BG_COLOR = QColor.fromRgb(255, 0, 0, 150)

SEND_INDICATOR_COLOR = QColor("darkblue")  # overwritten by system color (bin/urh)

# ROI-SELECTION COLORS
SELECTION_COLOR = QColor("darkblue")  # overwritten by system color (bin/urh)
NOISE_COLOR = QColor("red")
SELECTION_OPACITY = 1
NOISE_OPACITY = 0.33

# SEPARATION COLORS
ONES_AREA_COLOR = Qt.green
ZEROS_AREA_COLOR = Qt.magenta
SEPARATION_OPACITY = 0.15
SEPARATION_PADDING = 0.05  # percent

# PROTOCOL TABLE COLORS
SELECTED_ROW_COLOR = QColor.fromRgb(0, 0, 255)
DIFFERENCE_CELL_COLOR = QColor.fromRgb(255, 0, 0)

PROPERTY_FOUND_COLOR = QColor.fromRgb(0, 124, 0, 100)
PROPERTY_NOT_FOUND_COLOR = QColor.fromRgb(124, 0, 0, 100)

SEPARATION_ROW_HEIGHT = 30

PROJECT_FILE = "URHProject.xml"
DECODINGS_FILE = "decodings.txt"
FIELD_TYPE_SETTINGS = os.path.realpath(
    os.path.join(get_qt_settings_filename(), "..", "fieldtypes.xml")
)

# DEVICE SETTINGS
DEFAULT_IP_USRP = "192.168.10.2"
DEFAULT_IP_RTLSDRTCP = "127.0.0.1"

# DECODING NAMES
DECODING_INVERT = "Invert"
DECODING_DIFFERENTIAL = "Differential Encoding"
DECODING_REDUNDANCY = "Remove Redundancy"
DECODING_DATAWHITENING = "Remove Data Whitening (CC1101)"
DECODING_CARRIER = "Remove Carrier"
DECODING_BITORDER = "Change Bitorder"
DECODING_EDGE = "Edge Trigger"
DECODING_SUBSTITUTION = "Substitution"
DECODING_EXTERNAL = "External Program"
DECODING_ENOCEAN = "Wireless Short Packet (WSP)"
DECODING_CUT = "Cut before/after"
DECODING_MORSE = "Morse Code"
DECODING_DISABLED_PREFIX = "[Disabled] "

LABEL_COLORS = [
    QColor.fromRgb(217, 240, 27, 125),  # yellow
    QColor.fromRgb(41, 172, 81, 125),  # green
    QColor.fromRgb(245, 12, 12, 125),  # red
    QColor.fromRgb(12, 12, 242, 125),  # blue
    QColor.fromRgb(67, 44, 14, 125),  # brown
    QColor.fromRgb(146, 49, 49, 125),  # dark red
    QColor.fromRgb(9, 9, 54, 125),  # dark blue
    QColor.fromRgb(17, 49, 27, 125),  # dark green
    QColor.fromRgb(244, 246, 36, 125),  # strong yellow
    QColor.fromRgb(61, 67, 67, 125),  # gray 3
    QColor.fromRgb(58, 60, 100, 125),  # halfdark blue
    QColor.fromRgb(139, 148, 148, 125),  # gray 2
    QColor.fromRgb(153, 207, 206, 125),  # light blue green
    QColor.fromRgb(207, 223, 223, 125),  # gray 1
    QColor.fromRgb(106, 10, 10, 125),  # darker red
    QColor.fromRgb(12, 142, 242, 125),  # light blue
    QColor.fromRgb(213, 212, 134, 125),  # light yellow
    QColor.fromRgb(240, 238, 244, 125),  # gray 0
    QColor.fromRgb(201, 121, 18, 125),  # orange
    QColor.fromRgb(155, 170, 224, 125),  # lighter blue
    QColor.fromRgb(12, 242, 201, 125),  # blue green
    QColor.fromRgb(7, 237, 78, 125),  # light green
    QColor.fromRgb(154, 37, 111, 125),  # pink
    QColor.fromRgb(159, 237, 7, 125),  # yellow green
    QColor.fromRgb(231, 136, 242, 125),  # light pink
]

# full alpha for participant colors, since its used in text html view (signal frame)
PARTICIPANT_COLORS = [
    QColor.fromRgb(lc.red(), lc.green(), lc.blue()) for lc in LABEL_COLORS
]

BG_COLOR_CORRECT = QColor(0, 255, 0, 150)
BG_COLOR_WRONG = QColor(255, 0, 0, 150)

HIGHLIGHT_TEXT_BACKGROUND_COLOR = QColor("orange")
HIGHLIGHT_TEXT_FOREGROUND_COLOR = QColor("white")

PEAK_COLOR = QColor("darkRed")

NUM_CENTERS = 16

SHORTEST_PREAMBLE_IN_BITS = 8
SHORTEST_CONSTANT_IN_BITS = 8

# used for displaying indented logs e.g. in simulation dialog
INDENT = 8

# Pause separator in message files
PAUSE_SEP = "/"


def read(key: str, default_value=None, type=str):
    val = __get_qt_settings().value(key, default_value)
    if val is None:
        val = type()

    if type is bool:
        val = str(val).lower()
        try:
            return bool(int(val))
        except ValueError:
            return str(val).lower() == "true"
    else:
        return type(val)


def write(key: str, value):
    __get_qt_settings().setValue(key, value)


def all_keys():
    return __get_qt_settings().allKeys()


def sync():
    __get_qt_settings().sync()


OVERWRITE_RECEIVE_BUFFER_SIZE = None  # for unit tests


def get_receive_buffer_size(
    resume_on_full_receive_buffer: bool, spectrum_mode: bool
) -> int:
    if OVERWRITE_RECEIVE_BUFFER_SIZE:
        return OVERWRITE_RECEIVE_BUFFER_SIZE

    if resume_on_full_receive_buffer:
        if spectrum_mode:
            num_samples = SPECTRUM_BUFFER_SIZE
        else:
            num_samples = SNIFF_BUFFER_SIZE
    else:
        # Take 60% of avail memory
        threshold = read("ram_threshold", 0.6, float)
        num_samples = threshold * (psutil.virtual_memory().available / 8)

    # Do not let it allocate too much memory on 32 bit
    if 8 * 2 * num_samples > sys.maxsize:
        num_samples = sys.maxsize // (8 * 2 * 1.5)
        logger.info("Correcting buffer size to {}".format(num_samples))

    logger.info(
        "Allocate receive buffer with {0}B".format(
            Formatter.big_value_with_suffix(num_samples * 8)
        )
    )
    return int(num_samples)
