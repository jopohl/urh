import sys

import os
import tempfile


def init_path():
    # Append script path at end to prevent conflicts in case of frozen interpreter
    sys.path.append(sys.path.pop(0))
