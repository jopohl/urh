import os

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

def trace_calls(frame, event, arg):
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == 'write':
        # Ignore write() calls from print statements
        return
    func_line_no = frame.f_lineno
    func_filename = co.co_filename
    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    if "urh" in caller_filename or "urh" in func_filename:
        if "logging" in caller_filename or "logging" in func_filename:
            return

        if "_test" in caller_filename or "_test" in func_filename:
            start = '\033[91m'
        else:
            start = "\033[0;32m"
        end = "\033[0;0m"
    else:
        start, end = "", ""

    print('%s Call to %s on line %s of %s from line %s of %s %s' % \
          (start, func_name, func_line_no, func_filename,
           caller_line_no, caller_filename, end))
    return


import sys


# sys.settrace(trace_calls)


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def short_wait(interval=1):
    app = QApplication.instance()
    app.processEvents()
    QTest.qWait(interval)
    app.processEvents()

f = os.readlink(__file__) if os.path.islink(__file__) else __file__
path = os.path.realpath(os.path.join(f, ".."))


def get_path_for_data_file(filename):
    return os.path.join(path, "data", filename)
