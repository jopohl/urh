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
    extensions = [Extension("hackrf", ["hackrf"+ext],
                            extra_compile_args=["-static", "-static-libgcc", OPEN_MP_FLAG],
                            extra_link_args=[OPEN_MP_FLAG], libraries=["hackrf"],
                            language=LANGUAGE)]

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