import os

import sys
import platform
from collections import defaultdict
from distutils import ccompiler

from setuptools import Extension


EXTENSIONS = []   # give extensions to build here


class ExtensionHelper(object):
    """
    Helper class for easy access of device extensions
    """
    DEVICES = {
        "hackrf": {"lib": "hackrf", "test_function": "hackrf_init"},
        "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_set_tuner_bandwidth"},
    }

    FALLBACKS = {
        "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_get_device_name"}
    }

    @classmethod
    def get_device_extensions(cls, use_cython: bool, library_dirs=None):
        library_dirs = [] if library_dirs is None else library_dirs

        cur_dir = os.path.dirname(os.path.realpath(__file__))
        include_dirs = [os.path.realpath(os.path.join(cur_dir, "includes"))]

        if sys.platform == "win32":
            if platform.architecture()[0] != "64bit":
                return []  # only 64 bit python supported for native device backends

            result = []
            lib_dir = os.path.realpath(os.path.join(cur_dir, "lib/win"))
            for dev_name, params in cls.DEVICES.items():
                result.append(cls.get_device_extension(dev_name, [params["lib"]], [lib_dir], include_dirs))

            return result

        if sys.platform == "darwin":
            # On Mac OS X clang is by default not smart enough to search in the lib dir
            # see: https://github.com/jopohl/urh/issues/173
            library_dirs.append("/usr/local/lib")

        result = []

        # None = automatic (depending on lib is installed)
        # 1 = install extension always
        # 0 = Do not install extension
        build_device_extensions = defaultdict(lambda: None)

        for dev_name in cls.DEVICES:
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

        sys.path.append(os.path.realpath(os.path.join(cur_dir, "lib")))

        compiler = ccompiler.new_compiler()
        for dev_name, params in cls.DEVICES.items():
            if build_device_extensions[dev_name] == 0:
                print("\nSkipping native {0} support\n".format(dev_name))
                continue
            if build_device_extensions[dev_name] == 1:
                print("\nEnforcing native {0} support\n".format(dev_name))
                result.append(
                    cls.get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, use_cython))
                continue

            if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                     include_dirs=include_dirs):
                print("\nFound {0} lib. Will compile with native {1} support\n".format(params["lib"], dev_name))
                result.append(
                    cls.get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, use_cython))
            elif dev_name in cls.FALLBACKS:
                print("Trying fallback for {0}".format(dev_name))
                params = cls.FALLBACKS[dev_name]
                dev_name += "_fallback"
                if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                         include_dirs=include_dirs):
                    print("\nFound fallback. Will compile with native {0} support\n".format(dev_name))
                    result.append(
                        cls.get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, use_cython))
            else:
                print("\nSkipping native support for {1}\n".format(params["lib"], dev_name))
            try:
                os.remove("a.out")  # Temp file for checking
            except OSError:
                pass

        return result

    @staticmethod
    def get_device_extension(dev_name: str, libraries: list, library_dirs: list, include_dirs: list, use_cython=False):
        file_ext = "pyx" if use_cython else "cpp"
        return Extension("urh.dev.native.lib." + dev_name,
                         ["src/urh/dev/native/lib/{0}.{1}".format(dev_name, file_ext)],
                         libraries=libraries, library_dirs=library_dirs,
                         include_dirs=include_dirs, language="c++")

if __name__ == "__main__":
    from setuptools import setup
    setup(
        name="urh",
        ext_modules=EXTENSIONS,
    )
