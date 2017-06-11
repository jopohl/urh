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
