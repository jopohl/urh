from PyQt5.QtGui import QFont, QFontInfo


def isFixedPitch(font: QFont) -> bool:
    fi = QFontInfo(font)
    return fi.fixedPitch()


def getMonospaceFont() -> QFont:
    font = QFont("monospace")
    if isFixedPitch(font): return font
    font.setStyleHint(QFont.Monospace)
    if isFixedPitch(font): return font
    font.setStyleHint(QFont.TypeWriter)
    if isFixedPitch(font): return font
    font.setFamily("courier")
    if isFixedPitch(font): return font
    return font
