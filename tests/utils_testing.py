import os

from PyQt5.QtWidgets import QApplication
import sys


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

f = os.readlink(__file__) if os.path.islink(__file__) else __file__
path = os.path.realpath(os.path.join(f, ".."))


def get_path_for_data_file(filename):
    return os.path.join(path, "data", filename)