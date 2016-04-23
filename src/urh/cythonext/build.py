import os
import shutil
import sys
import tempfile
from subprocess import call

sys.dont_write_bytecode = True
build_dir = os.path.join(tempfile.gettempdir(), "build")

def get_python3_interpreter():
    paths = os.get_exec_path()

    for p in paths:
        for prog in ["python3", "python.exe"]:
            attempt = os.path.join(p, prog)
            if os.path.isfile(attempt):
                return attempt

    return None

def main():
    python3 = get_python3_interpreter()

    call([python3, "setup.py", "build_ext",
          "--build-lib",
          os.path.join(build_dir, "result"),
          "--build-temp", build_dir])


if __name__ == "__main__":
    main()
