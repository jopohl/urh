import sys

import os
import tempfile


def init_path():
    # Append script path at end to prevent conflicts in case of frozen interpreter
    sys.path.append(sys.path.pop(0))

    try:
        with open(os.path.join(tempfile.gettempdir(), "gnuradio_path.txt"), "r") as f:
            gnuradio_path = f.read().strip()

        os.environ["PATH"] = os.path.join(gnuradio_path, "bin") + os.pathsep + os.environ["PATH"]
        sys.path.insert(0, os.path.join(gnuradio_path, "lib", "site-packages"))

    except IOError:
        pass
