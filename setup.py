import os
import sys
from distutils.core import setup, Extension
import numpy
import src.urh.version as version

if sys.platform == "win32":
    OPEN_MP_FLAG = "-openmp"
else:
    OPEN_MP_FLAG = "-fopenmp"

DEBUG = True
COMPILER_DIRECTIVES = {'language_level': 3,
                       'cdivision': True,
                       'wraparound': False,
                       'boundscheck': False,
                       'initializedcheck': False,
                       }

UI_SUBDIRS = ("actions", "delegates", "views")
PLUGINS = ("AmbleAnalyzer", "BlockBreak", "ZeroHide")
URH_DIR = "urh"


def get_packages():
    packages = [URH_DIR]

    for path in os.listdir(os.path.join("./src/", URH_DIR)):
        if path == "__pycache__":
            continue
        if os.path.isdir(os.path.join(os.path.join("./src/", URH_DIR), path)):
            packages.append(URH_DIR + "." + path)
        if path == "ui":
            for subdir in UI_SUBDIRS:
                packages.append(URH_DIR + "." + path + "." + subdir)
        if path == "plugins":
            for plugin in PLUGINS:
                packages.append(URH_DIR + "." + path + "." + plugin)

    return packages


def get_package_data():
    package_data = {}
    for plugin in PLUGINS:
        package_data["urh.plugins." + plugin] = ['settings.ui', "descr.txt"]

    return package_data

def get_ext_modules():
    ext = ".cpp"

    filenames = [os.path.splitext(f)[0] for f in os.listdir("src/urh/cythonext") if f.endswith(ext)]

    extensions = [Extension("urh.cythonext." + f, ["src/urh/cythonext/" + f + ext],
                            include_dirs=[numpy.get_include()],
                            extra_compile_args=["-static", "-static-libgcc", OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG],
                            language="c++") for f in filenames]

    return extensions

def get_dev_modules():
    # Todo: Check if lib is there, if yes add to extensions
    ext = ".cpp"
    filenames = [os.path.splitext(f)[0] for f in os.listdir("src/urh/dev/native/lib") if f.endswith(ext)]
    libs = {"hackrf": "hackrf"}

    extensions = [Extension("urh.dev.native.lib." + f, ["src/urh/dev/native/lib" + f + ext],
                        #include_dirs=[numpy.get_include()],
                        extra_compile_args=["-static", "-static-libgcc", OPEN_MP_FLAG],
                        libraries=[libs[f]],
                        extra_link_args=[OPEN_MP_FLAG],
                        language="c++") for f in filenames]
    return extensions

#import generate_ui
#generate_ui.gen # pyuic5 is not included in all python3-pyqt5 packages (e.g. ubuntu), therefore do not regenerate UI here

setup(
    name="Universal Radio Hacker",
    version=version.VERSION,
    description="Hacking wireless protocols made easy",
    author="Johannes Pohl",
    author_email="Johannes.Pohl90@gmail.com",
    package_dir={"": "src"},
    package_data=get_package_data(),
    packages=get_packages(),
    ext_modules=get_ext_modules() + get_dev_modules(),
    # data_files=[("data", "")],
        scripts=["bin/urh"], requires=['PyQt5', 'numpy']
)

# python setup.py sdist --> Source distribution
# python setup.py bdist --> Vorkompiliertes Package https://docs.python.org/3/distutils/builtdist.html
