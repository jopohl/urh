import tempfile
from distutils import ccompiler
from distutils.core import setup, Extension

import shutil

import os
import sys

import numpy

if sys.platform == "win32":
    OPEN_MP_FLAG = "-openmp"
else:
    OPEN_MP_FLAG = "-fopenmp"

DEBUG = True
LANGUAGE = "c++" # c or c++
if DEBUG:
    COMPILER_DIRECTIVES = {'language_level': 3,
                           'cdivision': False,
                           'wraparound': True,
                           'boundscheck': True,
                           'initializedcheck': True,
                       }
else:
    COMPILER_DIRECTIVES = {'language_level': 3,
                           'cdivision': True,
                           'wraparound': False,
                           'boundscheck': False,
                           'initializedcheck': False,
                           }

build_dir = os.path.join(tempfile.gettempdir(), "build")


def get_device_modules():
    compiler = ccompiler.new_compiler()

    extensions = []
    devices = {
                "hackrf": {"lib": "hackrf", "test_function": "hackrf_init"}
              }

    for dev_name, params in devices.items():
        if compiler.has_function(params["test_function"], libraries=(params["lib"],)):
            print("\n\n\nFound {0}.h - will compile with native {1} support\n\n\n".format(params["lib"], dev_name))
            e = Extension(dev_name, ["{0}.cpp".format(dev_name)],
                          extra_compile_args= ["-static", "-static-libgcc", OPEN_MP_FLAG],
                          extra_link_args=[OPEN_MP_FLAG], language="c++",
                          libraries=[params["lib"]])
            extensions.append(e)
        else:
             print("\n\n\nCould not find {0}.h - skipping native support for {1}\n\n\n".format(params["lib"], dev_name))
        try:
            os.remove("a.out") # Temp file for checking
        except OSError:
            pass
    return extensions


def main():
    try:
        from Cython.Distutils import build_ext
    except ImportError:
        use_cython = False
    else:
        use_cython = True
    ext = '.pyx' if use_cython else '.cpp' if LANGUAGE == "c++" else ".c"
    filenames = [os.path.splitext(f)[0] for f in os.listdir() if f.endswith(ext)]

    extensions = [Extension(f, [f+ext],
                            include_dirs=[numpy.get_include()],
                            extra_compile_args=["-static", "-static-libgcc", OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG],
                            language=LANGUAGE) for f in filenames]

    if use_cython:
        from Cython.Build import cythonize
        extensions = cythonize(extensions, compiler_directives=COMPILER_DIRECTIVES)

    setup(
        name='Universal Radio Hacker',
        ext_modules=extensions
    )

    build_path = os.path.join(build_dir, "result")
    filenames = os.listdir(build_path)

    for f in filenames:
        shutil.move(os.path.join(build_path, f), f)


    # Part 2: Build devices
    DEV_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "dev", "native", "lib"))
    os.chdir(DEV_DIR)
    extensions = get_device_modules()

    if use_cython:
        from Cython.Build import cythonize
        extensions = cythonize(extensions, compiler_directives=COMPILER_DIRECTIVES)

    setup(
        name='Universal Radio Hacker',
        ext_modules=extensions
    )
    if os.path.isdir(os.path.join(DEV_DIR, "tmp")):
        shutil.rmtree(os.path.join(DEV_DIR, "tmp"))

    build_path = os.path.join(build_dir, "result")
    filenames = os.listdir(build_path)

    for f in filenames:
        shutil.move(os.path.join(build_path, f), f)

if __name__ == "__main__":
    main()