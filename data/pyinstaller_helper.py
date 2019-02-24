import os
import shutil
import sys
from multiprocessing.pool import Pool
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

shutil.copy(os.path.join(urh_path, "src/urh/main.py"), os.path.join(urh_path, "src/urh/urh.py"))
shutil.copy(os.path.join(urh_path, "src/urh/main.py"), os.path.join(urh_path, "src/urh/urh_debug.py"))
urh_cmd = cmd + ["--windowed", os.path.join(urh_path, "src/urh/urh.py")]
urh_debug_cmd = cmd + [os.path.join(urh_path, "src/urh/urh_debug.py")]
cli_cmd = cmd + [os.path.join(urh_path, "src/urh/cli/urh_cli.py")]


def run_cmd(cmd_list: list):
    cmd = " ".join(cmd_list)
    print(cmd)
    sys.stdout.flush()
    os.system(cmd)


with Pool(3) as p:
    p.map(run_cmd, [urh_cmd, cli_cmd, urh_debug_cmd])


shutil.copy("./pyinstaller/urh_cli/urh_cli.exe", "./pyinstaller/urh/urh_cli.exe")
shutil.copy("./pyinstaller/urh_debug/urh_debug.exe", "./pyinstaller/urh/urh_debug.exe")
