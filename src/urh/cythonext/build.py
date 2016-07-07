import os
import sys
import tempfile
from subprocess import call

sys.dont_write_bytecode = True
build_dir = os.path.join(tempfile.gettempdir(), "build")

def main():
    call([sys.executable, "setup.py", "build_ext",
          "--build-lib",
          os.path.join(build_dir, "result"),
          "--build-temp", build_dir])


if __name__ == "__main__":
    main()
