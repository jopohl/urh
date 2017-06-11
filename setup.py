import os
import sys

if sys.version_info < (3, 4):
    print("You need at least Python 3.4 for this application!")
    if sys.version_info[0] < 3:
        print("try running with python3 {}".format(" ".join(sys.argv)))
    sys.exit(1)

try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    print("Could not find setuptools")
    print("Try installing them with pip install setuptools")
    sys.exit(1)

from src.urh.dev.native import ExtensionHelper
import src.urh.version as version

if sys.platform == "win32":
    OPEN_MP_FLAG = "/openmp"
elif sys.platform == "darwin":
    OPEN_MP_FLAG = ""  # no OpenMP support in default Mac OSX compiler
else:
    OPEN_MP_FLAG = "-fopenmp"

COMPILER_DIRECTIVES = {'language_level': 3,
                       'cdivision': True,
                       'wraparound': False,
                       'boundscheck': False,
                       'initializedcheck': False,
                       }

UI_SUBDIRS = ("actions", "delegates", "views")
PLUGINS = [path for path in os.listdir("src/urh/plugins") if os.path.isdir(os.path.join("src/urh/plugins", path))]
URH_DIR = "urh"

try:
    import Cython.Build
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True
EXT = '.pyx' if USE_CYTHON else '.cpp'


class build_ext(_build_ext):
    def finalize_options(self):
        print("Finalizing options")
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


def get_packages():
    packages = [URH_DIR]
    separator = os.path.normpath("/")
    for dirpath, dirnames, filenames in os.walk(os.path.join("./src/", URH_DIR)):
        package_path = os.path.relpath(dirpath, os.path.join("./src/", URH_DIR)).replace(separator, ".")
        if len(package_path) > 1:
            packages.append(URH_DIR + "." + package_path)

    return packages


def get_package_data():
    package_data = {"urh.cythonext": ["*.cpp", "*.pyx"]}
    for plugin in PLUGINS:
        package_data["urh.plugins." + plugin] = ['*.ui', "*.txt"]

    package_data["urh.dev.native.lib"] = ["*.cpp", "*.c", "*.pyx", "*.pxd"]

    # Bundle headers
    package_data["urh.dev.native.includes"] = ["*.h"]
    include_dir = "src/urh/dev/native/includes"
    for dirpath, dirnames, filenames in os.walk(include_dir):
        for dir_name in dirnames:
            rel_dir_path = os.path.relpath(os.path.join(dirpath, dir_name), include_dir)
            package_data["urh.dev.native.includes."+rel_dir_path.replace(os.sep, ".")] = ["*.h"]

    is_release = os.path.isfile("/tmp/urh_releasing")

    if sys.platform == "win32" or is_release:
        # we use precompiled device backends on windows
        # only deploy DLLs on Windows or in release mode to prevent deploying by linux package managers
        package_data["urh.dev.native.lib.win.x64"] = ["*"]
        package_data["urh.dev.native.lib.win.x86"] = ["*"]

    return package_data


def get_ext_modules():
    filenames = [os.path.splitext(f)[0] for f in os.listdir("src/urh/cythonext") if f.endswith(EXT)]

    extensions = [Extension("urh.cythonext." + f, ["src/urh/cythonext/" + f + EXT],
                            extra_compile_args=[OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG],
                            language="c++") for f in filenames]

    return extensions


def read_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError, RuntimeError):
        return ""

install_requires = ["numpy", "psutil", "pyzmq"]
try:
    import PyQt5
except ImportError:
    install_requires.append("pyqt5")

if sys.version_info < (3, 4):
    install_requires.append('enum34')

ExtensionHelper.USE_RELATIVE_PATHS = True
extensions = get_ext_modules() + ExtensionHelper.get_device_extensions(USE_CYTHON)

if USE_CYTHON:
    from Cython.Build import cythonize

    extensions = cythonize(extensions, compiler_directives=COMPILER_DIRECTIVES)

setup(
    name="urh",
    version=version.VERSION,
    description="Universal Radio Hacker: investigate wireless protocols like a boss",
    long_description=read_long_description(),
    author="Johannes Pohl",
    author_email="Johannes.Pohl90@gmail.com",
    package_dir={"": "src"},
    package_data=get_package_data(),
    url="https://github.com/jopohl/urh",
    license="GNU General Public License (GPL)",
    download_url="https://github.com/jopohl/urh/tarball/v" + str(version.VERSION),
    install_requires=install_requires,
    setup_requires=['numpy'],
    packages=get_packages(),
    ext_modules=extensions,
    cmdclass={'build_ext': build_ext},
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'urh = urh.main:main',
        ]}
)

# python setup.py sdist --> Source distribution
# python setup.py bdist --> Vorkompiliertes Package https://docs.python.org/3/distutils/builtdist.html
