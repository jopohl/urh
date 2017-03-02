import os
import sys
import platform
from collections import defaultdict

if sys.version_info < (3, 4):
    print("You need at least Python 3.4 for this application!")
    sys.exit(1)

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

    is_release = os.path.isfile("/tmp/urh_releasing")  # make sure precompiled binding are uploaded to PyPi

    package_data["urh.dev.native.lib"] = ["*.cpp", "*.pyx", "*.pxd"]

    # Bundle headers
    package_data["urh.dev.native.includes"] = ["*.h"]
    package_data["urh.dev.native.includes.libhackrf"] = ["*.h"]

    if sys.platform == "win32" or is_release:
        # we use precompiled device backends on windows
        package_data["urh.dev.native.lib.win"] = ["*"]

    return package_data


def get_ext_modules():
    filenames = [os.path.splitext(f)[0] for f in os.listdir("src/urh/cythonext") if f.endswith(EXT)]

    extensions = [Extension("urh.cythonext." + f, ["src/urh/cythonext/" + f + EXT],
                            extra_compile_args=[OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG],
                            language="c++") for f in filenames]

    return extensions


def __get_device_extension(dev_name: str, libraries: list, library_dirs: list, include_dirs: list, use_cython=False):
    file_ext = "pyx" if use_cython else "cpp"
    return Extension("urh.dev.native.lib." + dev_name, ["src/urh/dev/native/lib/{0}.{1}".format(dev_name, file_ext)],
                     libraries=libraries, library_dirs=library_dirs,
                     include_dirs=include_dirs, language="c++")


def get_device_modules():
    include_dir = os.path.realpath(os.path.join(os.curdir, "src/urh/dev/native/includes"))
    devices = {
        "hackrf": {"lib": "hackrf", "test_function": "hackrf_init"},
        "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_set_tuner_bandwidth"},
    }

    fallbacks = {
        "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_get_device_name"}
    }

    if sys.platform == "win32":
        if platform.architecture()[0] != "64bit":
            return []  # only 64 bit python supported for native device backends

        result = []
        lib_dir = os.path.realpath(os.path.join(os.curdir, "src/urh/dev/native/lib/win"))
        for dev_name, params in devices.items():
            result.append(__get_device_extension(dev_name, [params["lib"]], [lib_dir], [include_dir]))

        return result

    if sys.platform == "darwin":
        # On Mac OS X clang is by default not smart enough to search in the lib dir
        # see: https://github.com/jopohl/urh/issues/173
        library_dirs = ["/usr/local/lib"]
    else:
        library_dirs = []

    result = []

    # None = automatic (depending on lib is installed)
    # 1 = install extension always
    # 0 = Do not install extension
    build_device_extensions = defaultdict(lambda: None)

    for dev_name in devices:
        with_option = "--with-" + dev_name
        without_option = "--without-" + dev_name

        if with_option in sys.argv and without_option in sys.argv:
            print("ambiguous options for " + dev_name)
            sys.exit(1)
        elif without_option in sys.argv:
            build_device_extensions[dev_name] = 0
            sys.argv.remove(without_option)
        elif with_option in sys.argv:
            build_device_extensions[dev_name] = 1
            sys.argv.remove(with_option)

    script_dir = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(os.path.realpath(os.path.join(script_dir, "src", "urh", "dev", "native", "lib")))

    compiler = ccompiler.new_compiler()
    for dev_name, params in devices.items():
        if build_device_extensions[dev_name] == 0:
            print("\nSkipping native {0} support\n".format(dev_name))
            continue
        if build_device_extensions[dev_name] == 1:
            print("\nEnforcing native {0} support\n".format(dev_name))
            result.append(__get_device_extension(dev_name, [params["lib"]], library_dirs, [include_dir], USE_CYTHON))
            continue

        if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                 include_dirs=[include_dir]):
            print("\nFound {0} lib. Will compile with native {1} support\n".format(params["lib"], dev_name))
            result.append(__get_device_extension(dev_name, [params["lib"]], library_dirs, [include_dir], USE_CYTHON))
        elif dev_name in fallbacks:
            print("Trying fallback for {0}".format(dev_name))
            params = fallbacks[dev_name]
            dev_name += "_fallback"
            if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                     include_dirs=[include_dir]):
                print("\nFound fallback. Will compile with native {0} support\n".format(dev_name))
                result.append(
                    __get_device_extension(dev_name, [params["lib"]], library_dirs, [include_dir], USE_CYTHON))
        else:
            print("\nSkipping native support for {1}\n".format(params["lib"], dev_name))
        try:
            os.remove("a.out")  # Temp file for checking
        except OSError:
            pass

    return result


def read_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError, RuntimeError):
        return ""


# import generate_ui
# generate_ui.gen # pyuic5 is not included in all python3-pyqt5 packages (e.g. ubuntu), therefore do not regenerate UI here

install_requires = ["numpy", "psutil", "pyzmq"]
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
    description="Universal Radio Hacker: investigate wireless protocols like a boss",
    long_description=read_long_description(),
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
