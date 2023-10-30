#!/usr/bin/env python3

import locale
import multiprocessing
import os
import re
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QStyleFactory

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error as e:
    print("Ignoring locale error {}".format(e))

GENERATE_UI = True


def fix_windows_stdout_stderr():
    """
    Processes can't write to stdout/stderr on frozen windows apps because they do not exist here
    if process tries it anyway we get a nasty dialog window popping up, so we redirect the streams to a dummy
    see https://github.com/jopohl/urh/issues/370
    """

    if hasattr(sys, "frozen") and sys.platform == "win32":
        try:
            sys.stdout.write("\n")
            sys.stdout.flush()
        except:

            class DummyStream(object):
                def __init__(self):
                    pass

                def write(self, data):
                    pass

                def read(self, data):
                    pass

                def flush(self):
                    pass

                def close(self):
                    pass

            sys.stdout, sys.stderr, sys.stdin = (
                DummyStream(),
                DummyStream(),
                DummyStream(),
            )
            sys.__stdout__, sys.__stderr__, sys.__stdin__ = (
                DummyStream(),
                DummyStream(),
                DummyStream(),
            )


def main():
    fix_windows_stdout_stderr()

    if sys.version_info < (3, 4):
        print("You need at least Python 3.4 for this application!")
        sys.exit(1)

    urh_exe = sys.executable if hasattr(sys, "frozen") else sys.argv[0]
    urh_exe = os.readlink(urh_exe) if os.path.islink(urh_exe) else urh_exe

    urh_dir = os.path.join(os.path.dirname(os.path.realpath(urh_exe)), "..", "..")
    prefix = os.path.abspath(os.path.normpath(urh_dir))

    src_dir = os.path.join(prefix, "src")
    if (
        os.path.exists(src_dir)
        and not prefix.startswith("/usr")
        and not re.match(r"(?i)c:\\program", prefix)
    ):
        # Started locally, not installed -> add directory to path
        sys.path.insert(0, src_dir)

    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        import urh.version

        print(urh.version.VERSION)
        sys.exit(0)

    if GENERATE_UI and not hasattr(sys, "frozen"):
        try:
            sys.path.insert(0, prefix)
            from data import generate_ui

            generate_ui.gen()
        except (ImportError, FileNotFoundError):
            # The generate UI script cannot be found so we are most likely in release mode, no problem here.
            pass

    from urh.util import util

    util.set_shared_library_path()

    try:
        import urh.cythonext.signal_functions
        import urh.cythonext.path_creator
        import urh.cythonext.util
    except ImportError:
        if hasattr(sys, "frozen"):
            print("C++ Extensions not found. Exiting...")
            sys.exit(1)
        print("Could not find C++ extensions, trying to build them.")
        old_dir = os.path.realpath(os.curdir)
        os.chdir(os.path.join(src_dir, "urh", "cythonext"))

        from urh.cythonext import build

        build.main()

        os.chdir(old_dir)

    from urh.controller.MainController import MainController
    from urh import settings

    if settings.read("theme_index", 0, int) > 0:
        os.environ["QT_QPA_PLATFORMTHEME"] = "fusion"

    app = QApplication(["URH"] + sys.argv[1:])
    app.setWindowIcon(QIcon(":/icons/icons/appicon.png"))

    try:
        app.styleHints().setShowShortcutsInContextMenus(True)
    except AttributeError:
        pass

    util.set_icon_theme()

    font_size = settings.read("font_size", 0, float)
    if font_size > 0:
        font = app.font()
        font.setPointSizeF(font_size)
        app.setFont(font)

    settings.write("default_theme", app.style().objectName())

    if settings.read("theme_index", 0, int) > 0:
        app.setStyle(QStyleFactory.create("Fusion"))

        if settings.read("theme_index", 0, int) == 2:
            palette = QPalette()
            background_color = QColor(56, 60, 74)
            text_color = QColor(211, 218, 227).lighter()
            palette.setColor(QPalette.Window, background_color)
            palette.setColor(QPalette.WindowText, text_color)
            palette.setColor(QPalette.Base, background_color)
            palette.setColor(QPalette.AlternateBase, background_color)
            palette.setColor(QPalette.ToolTipBase, background_color)
            palette.setColor(QPalette.ToolTipText, text_color)
            palette.setColor(QPalette.Text, text_color)

            palette.setColor(QPalette.Button, background_color)
            palette.setColor(QPalette.ButtonText, text_color)

            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)

            palette.setColor(QPalette.Highlight, QColor(200, 50, 0))
            palette.setColor(QPalette.HighlightedText, text_color)
            app.setPalette(palette)

    # use system colors for painting
    widget = QWidget()
    bg_color = widget.palette().color(QPalette.Background)
    fg_color = widget.palette().color(QPalette.Foreground)
    selection_color = widget.palette().color(QPalette.Highlight)
    settings.BGCOLOR = bg_color
    settings.LINECOLOR = fg_color
    settings.SELECTION_COLOR = selection_color
    settings.SEND_INDICATOR_COLOR = selection_color

    main_window = MainController()
    # allow usage of prange (OpenMP) in Processes
    multiprocessing.set_start_method("spawn")

    if sys.platform == "win32":
        # Ensure we get the app icon in windows taskbar
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("jopohl.urh")

    if settings.read("MainController/geometry", type=bytes):
        main_window.show()
    else:
        main_window.showMaximized()

    if "autoclose" in sys.argv[1:]:
        # Autoclose after 1 second, this is useful for automated testing
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(1000)

    return_code = app.exec_()
    app.closeAllWindows()
    os._exit(
        return_code
    )  # sys.exit() is not enough on Windows and will result in crash on exit


if __name__ == "__main__":
    if hasattr(sys, "frozen"):
        multiprocessing.freeze_support()

    main()
