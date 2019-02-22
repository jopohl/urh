import os
import sys
from subprocess import call

HIDDEN_IMPORTS = ["packaging.specifiers", "packaging.requirements", "numpy.core._methods",
                  "numpy.core._dtype_ctyaddpes"]
DATA = [("src/urh/dev/native/lib/shared", "."), ("src/urh/plugins", "urh/plugins"), ]
EXCLUDE = ["matplotlib"]

cmd = ["pyinstaller", "--windowed"]
if sys.platform == "darwin":
    cmd.append("--onefile")

for hidden_import in HIDDEN_IMPORTS:
    cmd.append("--hidden-import={}".format(hidden_import))

for src, dst in DATA:
    cmd.append("--add-data")
    cmd.append('"{}{}{}"'.format(src, os.pathsep, dst))

for exclude in EXCLUDE:
    cmd.append("--exclude-module={}".format(exclude))

urh_path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
cmd.append('--icon="{}"'.format(os.path.join(urh_path, "data/icons/appicon.ico")))

os.rename(os.path.join(urh_path, "src/urh/main.py"), os.path.join(urh_path, "src/urh/urh.py"))
cmd.append(os.path.join(urh_path, "src/urh/urh.py"))
cmd = " ".join(cmd)
print(cmd)
call(cmd, shell=True)

if sys.platform == "win32":
    os.rename("./dist/urh", "./dist/urh-x{}".format(64 if sys.maxsize > 2**32 else 86))
