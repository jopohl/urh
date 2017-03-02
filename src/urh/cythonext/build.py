import os
import sys
import tempfile
from subprocess import call

build_dir = os.path.join(tempfile.gettempdir(), "build")


def main():
    cur_dir = os.path.realpath(__file__)
    os.chdir(os.path.realpath(os.path.join(cur_dir, "..", "..", "..", "..")))
    call([sys.executable, "setup.py", "build_ext", "--inplace"])


if __name__ == "__main__":
    main()
