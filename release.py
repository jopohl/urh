import os
import sys
from subprocess import call, check_output

import pytest
from urh import constants
from urh.util.Logger import logger

open("/tmp/urh_releasing", "w").close()

script_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))

rc = pytest.main(["--exitfirst", "tests"])

if rc != 0:
    print(constants.color.RED + constants.color.BOLD + "Unittests failed. Abort release." + constants.color.END)
    sys.exit(1)

# -n for parallel with pytest-xdist
rc = pytest.main(["-v", "-n", "3", "tests/TestInstallation.py"])

if rc != 0:
    print(constants.color.BOLD + constants.color.RED + "Installation Test failed. Abort release." + constants.color.END)
    sys.exit(1)

# Generate Readme for PyPi (RST)
try:
    rc = call("pandoc --from=markdown --to=rst --output=README README.md", shell=True)
except:
    rc = 1

if rc != 0:
    logger.warning("Could not generate rst docs. Is pandoc installed?")

from src.urh import version
version_file = os.path.realpath(os.path.join(script_dir, "src", "urh", "version.py"))

cur_version = version.VERSION
numbers = cur_version.split(".")
numbers[-1] = str(int(numbers[-1]) + 1)
cur_version = ".".join(numbers)

with open(version_file, "w") as f:
    f.write('VERSION = "{0}" \n'.format(cur_version))

# Publish new version number
os.chdir(script_dir)
call(["git", "commit", "-am", "version" + cur_version])
call(["git", "push"])

# Publish to PyPi
os.chdir(script_dir)
call(["git", "tag", "v"+cur_version, "-m", "version "+cur_version])
call(["git", "push", "origin", "--tags"]) # Creates tar package on https://github.com/jopohl/urh/tarball/va.b.c.d
call(["python", "setup.py", "register", "-r", "pypi"])
call(["python", "setup.py", "sdist", "upload", "-r", "pypi"])

# Publish to AUR
# Adapt pkgver
# Regenerate md5sum and sha256sum
import tempfile, shutil, fileinput
os.chdir(tempfile.gettempdir())
call(["wget", "https://github.com/jopohl/urh/tarball/v"+cur_version])
md5sum = check_output(["md5sum", "v"+cur_version]).decode("ascii").split(" ")[0]
sha256sum = check_output(["sha256sum", "v"+cur_version]).decode("ascii").split(" ")[0]
print("md5sum", md5sum)
print("sha256sum", sha256sum)


shutil.rmtree("aur", ignore_errors=True)
os.mkdir("aur")
os.chdir("aur")
call(["git", "clone", "git+ssh://aur@aur.archlinux.org/urh.git"])
os.chdir("urh")

for line in fileinput.input("PKGBUILD", inplace=True):
    if line.startswith("pkgver="):
        print("pkgver="+cur_version)
    elif line.startswith("md5sums="):
        print("md5sums=('"+md5sum+"')")
    elif line.startswith("sha256sums="):
        print("sha256sums=('"+sha256sum+"')")
    else:
        print(line, end="")

call("makepkg --printsrcinfo > .SRCINFO", shell=True)
call(["git", "commit", "-am", "version "+cur_version])
call(["git", "push"])

os.remove("/tmp/urh_releasing")

os.chdir(script_dir)
rc = pytest.main(["-v", "-n", "3", "tests/TestInstallation.py"])

if rc != 0:
    print(constants.color.BOLD + constants.color.RED + "Installation Test failed." + constants.color.END)
else:
    print(constants.color.BOLD + constants.color.GREEN + "Success" + constants.color.END)
