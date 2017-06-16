#!/usr/bin/env python3

import locale
import re
import time
import os
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QStyleFactory

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error as e:
    print("Ignoring locale error {}".format(e))

GENERATE_UI = True


def main():
    if sys.version_info < (3, 4):
        print("You need at least Python 3.4 for this application!")
        sys.exit(1)

    t = time.time()
    if GENERATE_UI and not hasattr(sys, 'frozen'):
        try:
            urh_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "..", ".."))
            sys.path.append(urh_dir)
            sys.path.append(os.path.join(urh_dir, "src"))

            import generate_ui

            generate_ui.gen()

            print("Time for generating UI: %.2f seconds" % (time.time() - t))
        except (ImportError, FileNotFoundError):
            print("Will not regenerate UI, because script can't be found. This is okay in release.")

    urh_exe = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
    urh_exe = os.readlink(urh_exe) if os.path.islink(urh_exe) else urh_exe

    urh_dir = os.path.join(os.path.dirname(os.path.realpath(urh_exe)), "..", "..")
    prefix = os.path.abspath(os.path.normpath(urh_dir))

    src_dir = os.path.join(prefix, "src")
    if os.path.exists(src_dir) and not prefix.startswith("/usr") and not re.match(r"(?i)c:\\program", prefix):
        # Started locally, not installed
        print("Adding {0} to pythonpath. This is only important when running URH from source.".format(src_dir))
        sys.path.insert(0, src_dir)

    from urh.util import util
    util.set_windows_lib_path()

    try:
        import urh.cythonext.signalFunctions
        import urh.cythonext.path_creator
        import urh.cythonext.util
    except ImportError:
        print("Could not find C++ extensions, trying to build them.")
        old_dir = os.curdir
        os.chdir(os.path.join(src_dir, "urh", "cythonext"))

        from urh.cythonext import build
        build.main()

        os.chdir(old_dir)

    from urh.controller.MainController import MainController
    from urh import constants

    if constants.SETTINGS.value("theme_index", 0, int) > 0:
        os.environ['QT_QPA_PLATFORMTHEME'] = 'fusion'

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/data/icons/appicon.png"))

    if sys.platform != "linux":
        # noinspection PyUnresolvedReferences
        import urh.ui.xtra_icons_rc
        QIcon.setThemeName("oxy")

    constants.SETTINGS.setValue("default_theme", app.style().objectName())

    if constants.SETTINGS.value("theme_index", 0, int) > 0:
        app.setStyle(QStyleFactory.create("Fusion"))

        if constants.SETTINGS.value("theme_index", 0, int) == 2:
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

    main_window = MainController()

    if sys.platform == "darwin":
        menu_bar = main_window.menuBar()
        menu_bar.setNativeMenuBar(False)
        import multiprocessing as mp
        mp.set_start_method("spawn")  # prevent errors with forking in native RTL-SDR backend

    main_window.showMaximized()
    # main_window.setFixedSize(1920, 1080 - 30)  # Youtube

    # use system colors for painting
    widget = QWidget()
    bgcolor = widget.palette().color(QPalette.Background)
    fgcolor = widget.palette().color(QPalette.Foreground)
    selection_color = widget.palette().color(QPalette.Highlight)
    constants.BGCOLOR = bgcolor
    constants.LINECOLOR = fgcolor
    constants.SELECTION_COLOR = selection_color
    constants.SEND_INDICATOR_COLOR = selection_color

    if "autoclose" in sys.argv[1:]:
        # Autoclose after 1 second, this is useful for automated testing
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(1000)

    return_code = app.exec_()
    app.closeAllWindows()
    os._exit(return_code)  # sys.exit() is not enough on Windows and will result in crash on exit


if __name__ == "__main__":
    main()
