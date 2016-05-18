#QT5 = True

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor

MAX_RECENT_FILE_NR = 10
MAX_DISPLAYED_SAMPLES = 1000000
MIN_DISPLAYED_SAMPLES = 300
ZOOM_TICKS = 10

PIXELS_PER_PATH = 1000

PAUSE_TRESHOLD = 10
RECT_BIT_WIDTH = 10
BIT_SCENE_HEIGHT = 100

TRANSPARENT_COLOR = QColor(Qt.transparent)

LINECOLOR = QColor.fromRgb(225, 225, 225)
BGCOLOR = QColor.fromRgb(55, 53, 53)
AXISCOLOR = QColor.fromRgb(200, 200, 200, 100)
NOISELINECOLOR = QColor.fromRgb(255, 107, 104)
ARROWCOLOR = QColor.fromRgb(204, 120, 50)

# ROI-SELECTION COLORS
SELECTION_COLOR = QColor("orange")
NOISE_COLOR = QColor("red")
SELECTION_OPACITY = 0.4

# SEPARATION COLORS
ONES_AREA_COLOR = QColor.fromRgb(0, 128, 128)
ZEROS_AREA_COLOR = QColor.fromRgb(90, 9, 148)
SEPARATION_OPACITY = 0.2
SEPARATION_PADDING = .05  # Prozent

# PROTOCOL TABLE COLORS
SELECTED_ROW_COLOR = QColor.fromRgb(0, 0, 255)
DIFFERENCE_CELL_COLOR = QColor.fromRgb(255, 0, 0)

PROPERTY_FOUND_COLOR = QColor.fromRgb(0, 124, 0, 100)
PROPERTY_NOT_FOUND_COLOR = QColor.fromRgb(124, 0, 0, 100)

SEPARATION_ROW_HEIGHT = 30

SETTINGS = QSettings(QSettings.UserScope, 'urh', 'urh')
PROJECT_FILE = "URHProject.xml"
DECODINGS_FILE = "decodings.txt"

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
DECODING_DISABLED_PREFIX = "[Disabled] "

LABEL_COLORS = [QColor.fromRgb(255, 255, 0, 75), QColor.fromRgb(244, 164, 96, 75),
                QColor.fromRgb(0, 255, 255, 75), QColor.fromRgb(255, 0, 255, 75),
                QColor.fromRgb(255, 0, 0, 75), QColor.fromRgb(0, 255, 0, 75),
                QColor.fromRgb(0, 0, 255, 75), QColor.fromRgb(205, 38, 38, 75),
                QColor.fromRgb(105, 105, 105, 150)]

PARTICIPANT_COLORS = LABEL_COLORS[:]

HIGHLIGHT_TEXT_BACKGROUND_COLOR = QColor("orange")
HIGHLIGHT_TEXT_FOREGROUND_COLOR = QColor("white")

PEAK_COLOR = QColor("darkRed")

# SYMBOL PARAMETERS
SYMBOL_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                "<", ">", "|", ",", ".", "-", "_", "@", "*", "+", "~", "#", "§",
                "²", "³", '"', "$", "%", "&", "/", "{", "(", "[", ")", "]", "=",
                "}", "ß", "?", "`", "¸", "€", "µ", "^", "°", "☠", "♫", "®", "☢"]


NUM_CENTERS = 16