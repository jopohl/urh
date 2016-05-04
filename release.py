from subprocess import call
import os, sys

script_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
sys.path.append(script_dir)

from src.urh import version

version_file = os.path.realpath(os.path.join(script_dir, "src", "urh", "version.py"))

cur_version = version.VERSION
numbers = cur_version.split(".")
numbers[-1] = str(int(numbers[-1]) + 1)
cur_version = ".".join(numbers)

with open(version_file, "w") as f:
    f.write('VERSION = "{0}" \n'.format(cur_version))

# Publish to PyPi
os.chdir(script_dir)
call(["git", "tag", "v"+cur_version, "-m", "version "+cur_version])
call(["git", "push", "origin", "--tags"]) # Creates tar package on https://github.com/jopohl/urh/tarball/va.b.c.d
call(["python", "setup.py", "register", "-r", "pypi"])
call(["python", "setup.py", "sdist", "upload", "-r", "pypi"])

# Publish to AUR
import tempfile
os.chdir(tempfile.gettempdir())
call(["git"])