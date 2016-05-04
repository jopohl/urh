import os, sys

script_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
sys.path.append(script_dir)

from src.urh import version

version_file = os.path.realpath(os.path.join(script_dir, "src", "urh", "version.py"))

cur_version = version.VERSION
numbers = cur_version.split(".")
numbers[-1] = str(int(numbers[-1]) + 1)
cur_version = ".".join(numbers)
print(cur_version)