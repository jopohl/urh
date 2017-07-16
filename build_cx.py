import os
import sys

import cx_Freeze

import src.urh.version as version

def build_exe():
    # have to make sure args looks right
    sys.argv = sys.argv[:1] + ['build']

    app_path = os.path.join(os.path.dirname(__file__), "src", "urh", "main.py")
    include_files = [
        os.path.join("data", 'icons', 'appicon.png')
    ]

    if sys.platform == 'win32':
        arch = "x64" if sys.maxsize > 2 ** 32 else "x86"
        lib_path = os.path.join("src", "urh", "dev", "native", "lib", "win", arch)
        for f in os.listdir(lib_path):
            include_files.append(os.path.join(lib_path, f))

        executables = [cx_Freeze.Executable(
            app_path,
            targetName="urh.exe",
            icon=os.path.join("data", 'icons', 'appicon.png'),
            base="Win32GUI")]
    else:
        executables = [cx_Freeze.Executable(
            app_path,
            targetName="urh",
            icon=os.path.join("data", 'icons', 'appicon.png'))]

    for f in os.listdir(os.path.join("src", "urh", "dev", "gr", "scripts")):
        if f.endswith(".py"):
            include_files.append(os.path.join("src", "urh", "dev", "gr", "scripts", f))

    options = {
        'build_exe': {
            "include_files": include_files,
            "include_msvcr": True,
            "excludes": ["tkinter"],
            "includes": ['numpy.core._methods', 'numpy.lib.format', 'six', 'appdirs',
                         'packaging', 'packaging.version', 'packaging.specifiers', 'packaging.requirements',
                         'setuptools.msvc']
        }
    }

    cx_Freeze.setup(
        name="Universal Radio Hacker",
        version=version.VERSION,
        executables=executables,
        options=options
    )

if __name__ == '__main__':
    build_exe()
