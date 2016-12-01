import os
import sys

try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    print("Could not find setuptools")
    print("Try installing them with pip install setuptools")
    sys.exit(1)

from distutils import ccompiler
import src.urh.version as version

if sys.platform == "win32":
    OPEN_MP_FLAG = "-openmp"
else:
    OPEN_MP_FLAG = "-fopenmp"


COMPILER_DIRECTIVES = {'language_level': 3,
                       'cdivision': True,
                       'wraparound': False,
                       'boundscheck': False,
                       'initializedcheck': False,
                       }

UI_SUBDIRS = ("actions", "delegates", "views")
PLUGINS = ("AmbleAnalyzer", "MessageBreak", "ZeroHide")
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
        print("Finalizing optonms")
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
    package_data = {}
    for plugin in PLUGINS:
        package_data["urh.plugins." + plugin] = ['settings.ui', "descr.txt"]

    is_release = os.path.isfile("/tmp/urh_releasing") # make sure precompiled binding are uploaded to PyPi

    if sys.platform == "win32" or is_release:
        # we use precompiled device backends on windows
        package_data["urh.dev.native.lib"] = ["hackrf.cp35-win_amd64.pyd"]

    return package_data


def get_ext_modules():
    filenames = [os.path.splitext(f)[0] for f in os.listdir("src/urh/cythonext") if f.endswith(EXT)]

    extensions = [Extension("urh.cythonext." + f, ["src/urh/cythonext/" + f + EXT],
                            extra_compile_args=["-static", "-static-libgcc", OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG],
                            language="c++") for f in filenames]

    return extensions


def get_device_modules():
    if sys.platform == "win32":
        # we use precompiled device backends on windows
        return []

    compiler = ccompiler.new_compiler()

    extensions = []
    devices = {
        "hackrf": {"lib": "hackrf", "test_function": "hackrf_init"}
    }

    scriptdir = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(os.path.realpath(os.path.join(scriptdir, "src", "urh", "dev", "native", "lib")))
    for dev_name, params in devices.items():
        if compiler.has_function(params["test_function"], libraries=(params["lib"],)):
            print("\n\n\nFound {0}.h - will compile with native {1} support\n\n\n".format(params["lib"], dev_name))
            e = Extension("urh.dev.native.lib." + dev_name, ["src/urh/dev/native/lib/{0}{1}".format(dev_name, EXT)],
                          extra_compile_args=["-static", "-static-libgcc", OPEN_MP_FLAG],
                          extra_link_args=[OPEN_MP_FLAG], language="c++",
                          libraries=[params["lib"]])
            extensions.append(e)
        else:
            print("\n\n\nCould not find {0}.h - skipping native support for {1}\n\n\n".format(params["lib"], dev_name))
        try:
            os.remove("a.out")  # Temp file for checking
        except OSError:
            pass
    return extensions


# import generate_ui
# generate_ui.gen # pyuic5 is not included in all python3-pyqt5 packages (e.g. ubuntu), therefore do not regenerate UI here

install_requires = ["numpy", "psutil"]
try:
    import PyQt5
except ImportError:
    install_requires.append("pyqt5")

if sys.version_info < (3, 4):
    install_requires.append('enum34')

extensions = get_ext_modules() + get_device_modules()

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, compiler_directives=COMPILER_DIRECTIVES)

setup(
    name="urh",
    version=version.VERSION,
    description="Universal Radio Hacker: Hacking wireless protocols made easy",
    author="Johannes Pohl",
    author_email="Johannes.Pohl90@gmail.com",
    package_dir={"": "src"},
    package_data=get_package_data(),
    url="https://github.com/jopohl/urh",
    license="Apache License 2.0",
    download_url="https://github.com/jopohl/urh/tarball/v" + str(version.VERSION),
    install_requires=install_requires,
    setup_requires=['numpy'],
    packages=get_packages(),
    ext_modules=get_ext_modules() + get_device_modules(),
    cmdclass={'build_ext':build_ext},
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'urh = urh.main:main',
        ]}
)

# python setup.py sdist --> Source distribution
# python setup.py bdist --> Vorkompiliertes Package https://docs.python.org/3/distutils/builtdist.html
