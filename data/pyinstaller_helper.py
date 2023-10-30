import os
import shutil
import sys

HIDDEN_IMPORTS = [
    "packaging.specifiers",
    "packaging.requirements",
    "pkg_resources.py2_warn",
    "numpy.core._methods",
    "numpy.core._dtype_ctypes",
    "numpy.random.common",
    "numpy.random.entropy",
    "numpy.random.bounded_integers",
]
DATA = [
    ("src/urh/dev/native/lib/shared", "."),
    ("src/urh/plugins", "urh/plugins"),
]
EXCLUDE = ["matplotlib"]


def run_pyinstaller(cmd_list: list, env: list = None):
    cmd = " ".join(cmd_list)
    print(cmd, flush=True)

    env = [] if env is None else env
    if env:
        os.system(" ".join(env) + " " + cmd)
    else:
        os.system(cmd)


if __name__ == "__main__":
    cmd = ["pyinstaller", "--clean"]
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

    if sys.platform == "darwin":
        cmd.append(
            '--icon="{}"'.format(os.path.join(urh_path, "data/icons/appicon.icns"))
        )
    else:
        cmd.append(
            '--icon="{}"'.format(os.path.join(urh_path, "data/icons/appicon.ico"))
        )

    cmd.extend(["--distpath", "./pyinstaller"])

    urh_cmd = cmd + [
        "--name=urh",
        "--windowed",
        "--workpath",
        "./urh_build",
        os.path.join(urh_path, "src/urh/main.py"),
    ]

    urh_debug_cmd = cmd + [
        "--name=urh_debug",
        "--workpath",
        "./urh_debug_build",
        os.path.join(urh_path, "src/urh/main.py"),
    ]

    cli_cmd = cmd + [
        "--workpath",
        "./urh_cli_build",
        os.path.join(urh_path, "src/urh/cli/urh_cli.py"),
    ]

    os.makedirs("./pyinstaller")
    if sys.platform == "darwin":
        run_pyinstaller(
            urh_cmd, env=["DYLD_LIBRARY_PATH=src/urh/dev/native/lib/shared"]
        )

        import plistlib

        with open("pyinstaller/urh.app/Contents/Info.plist", "rb") as f:
            p = plistlib.load(f)
        p["NSHighResolutionCapable"] = True
        p["NSRequiresAquaSystemAppearance"] = True
        p[
            "NSMicrophoneUsageDescription"
        ] = "URH needs access to your microphone to capture signals via Soundcard."
        with open("pyinstaller/urh.app/Contents/Info.plist", "wb") as f:
            plistlib.dump(p, f)

    else:
        for cmd in [urh_cmd, cli_cmd, urh_debug_cmd]:
            run_pyinstaller(cmd)

        shutil.copy(
            "./pyinstaller/urh_cli/urh_cli.exe", "./pyinstaller/urh/urh_cli.exe"
        )
        shutil.copy(
            "./pyinstaller/urh_debug/urh_debug.exe", "./pyinstaller/urh/urh_debug.exe"
        )
