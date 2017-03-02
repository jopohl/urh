#!/usr/bin/env python3

import locale
import re
import time
import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QStyleFactory

locale.setlocale(locale.LC_ALL, '')

GENERATE_UI = True


def main():
    if sys.version_info < (3, 4):
        print("You need at least Python 3.4 for this application!")
        sys.exit(1)

    if sys.platform == "win32":
        urh_dir = os.path.dirname(os.path.realpath(__file__)) if not os.path.islink(__file__) \
            else os.path.dirname(os.path.realpath(os.readlink(__file__)))
        assert os.path.isdir(urh_dir)

        dll_dir = os.path.realpath(os.path.join(urh_dir, "dev", "native", "lib", "win"))
        print("Using DLLs from:", dll_dir)
        os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']

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
            print("Will not regenerate UI, because script cant be found. This is okay in release.")

    urh_exe = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
    urh_exe = os.readlink(urh_exe) if os.path.islink(urh_exe) else urh_exe

    urh_dir = os.path.join(os.path.dirname(urh_exe), "..", "..")
    prefix = os.path.abspath(os.path.normpath(urh_dir))

    src_dir = os.path.join(prefix, "src")
    if os.path.exists(src_dir) and not prefix.startswith("/usr") \
            and not re.match(r"(?i)c:\\program", prefix):
        # Started locally, not installed
        print("Using modules from {0}".format(src_dir))
        sys.path.insert(0, src_dir)

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

    if constants.SETTINGS.value("use_fallback_theme", False, bool):
        os.environ['QT_QPA_PLATFORMTHEME'] = 'fusion'

    app = QApplication(sys.argv)

    # noinspection PyUnresolvedReferences
    import urh.ui.xtra_icons_rc  # Use oxy theme always
    QIcon.setThemeName("oxy")

    constants.SETTINGS.setValue("default_theme", QApplication.style().objectName())

    if constants.SETTINGS.value("use_fallback_theme", False, bool):
        QApplication.setStyle(QStyleFactory.create("Fusion"))

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

    os._exit(app.exec_())  # sys.exit() is not enough on Windows and will result in crash on exit


if __name__ == "__main__":
    main()
