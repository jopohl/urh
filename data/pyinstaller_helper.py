import os
import shutil
import sys
from subprocess import call

HIDDEN_IMPORTS = ["packaging.specifiers", "packaging.requirements",
                  "numpy.core._methods", "numpy.core._dtype_ctypes"]
DATA = [("src/urh/dev/native/lib/shared", "."), ("src/urh/plugins", "urh/plugins"), ]
EXCLUDE = ["matplotlib"]

cmd = ["pyinstaller"]
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

cmd.extend(["--distpath", "./pyinstaller"])

os.rename(os.path.join(urh_path, "src/urh/main.py"), os.path.join(urh_path, "src/urh/urh.py"))
urh_cmd = cmd + ["--windowed", os.path.join(urh_path, "src/urh/urh.py")]
cli_cmd = cmd + [os.path.join(urh_path, "src/urh/cli/urh_cli.py")]

for cmd in (urh_cmd, cli_cmd):
    cmd = " ".join(cmd)
    print(cmd)
    sys.stdout.flush()
    call(cmd, shell=True)

shutil.copy("./pyinstaller/urh_cli/urh_cli.exe", "./pyinstaller/urh/urh_cli.exe")
