import os
import sys
from cx_Freeze import setup, Executable
import src.urh.version as version
from distutils.core import Extension
#from src.urh.dev.native import ExtensionHelper
import tempfile

IS_RELEASE = os.path.isfile(os.path.join(tempfile.gettempdir(), "urh_releasing"))

if sys.platform == "win32":
    OPEN_MP_FLAG = "/openmp"
elif sys.platform == "darwin":
    OPEN_MP_FLAG = ""  # no OpenMP support in default Mac OSX compiler
else:
    OPEN_MP_FLAG = "-fopenmp"

def get_ext_modules():
    filenames = [os.path.splitext(f)[0] for f in os.listdir("src/urh/cythonext") if f.endswith(".cpp")]

    extensions = [Extension("urh.cythonext." + f, ["src/urh/cythonext/" + f + ".cpp"],
                            extra_compile_args=[OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG],
                            language="c++") for f in filenames]

    return extensions

def get_packages():
    packages = [".src/urh"]
    separator = os.path.normpath("/")
    for dirpath, dirnames, filenames in os.walk(os.path.join("./src/", "urh")):
        package_path = os.path.relpath(dirpath, os.path.join("./src/", "urh")).replace(separator, ".")
        if len(package_path) > 1:
            packages.append("./src/urh/" + package_path)

    return packages

def get_package_data():
    package_data = {"urh.cythonext": ["*.cpp", "*.pyx"]}
    for plugin in [path for path in os.listdir("src/urh/plugins") if os.path.isdir(os.path.join("src/urh/plugins", path))]:
        package_data["urh.plugins." + plugin] = ['*.ui', "*.txt"]

    package_data["urh.dev.native.lib"] = ["*.cpp", "*.c", "*.pyx", "*.pxd"]

    # Bundle headers
    package_data["urh.dev.native.includes"] = ["*.h"]
    include_dir = "src/urh/dev/native/includes"
    for dirpath, dirnames, filenames in os.walk(include_dir):
        for dir_name in dirnames:
            rel_dir_path = os.path.relpath(os.path.join(dirpath, dir_name), include_dir)
            package_data["urh.dev.native.includes."+rel_dir_path.replace(os.sep, ".")] = ["*.h"]

    if sys.platform == "win32" or IS_RELEASE:
        # we use precompiled device backends on windows
        # only deploy DLLs on Windows or in release mode to prevent deploying by linux package managers
        package_data["urh.dev.native.lib.win.x64"] = ["*"]
        package_data["urh.dev.native.lib.win.x86"] = ["*"]

    return package_data

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["traceback"], "path": sys.path+["/home/joe/GIT/urh/src"], "excludes": ["tkinter"]}



# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"


setup(
    name="urh",
    version=version.VERSION,
    description="Universal Radio Hacker: investigate wireless protocols like a boss",
    author="Johannes Pohl",
    author_email="Johannes.Pohl90@gmail.com",
    url="https://github.com/jopohl/urh",
    license="GNU General Public License (GPL)",
    download_url="https://github.com/jopohl/urh/tarball/v" + str(version.VERSION),
    ext_modules=get_ext_modules(), #+ ExtensionHelper.get_device_extensions(False),
    package_data=get_package_data(),
    package_dir={"": "src"},
    #packages=get_packages(),
    options={"build_exe": build_exe_options},
    executables = [Executable("src/urh/main.py", base = base)]
)
