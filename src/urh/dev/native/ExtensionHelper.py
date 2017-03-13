import os

import sys
import platform
from collections import defaultdict
from distutils import ccompiler

from setuptools import Extension


class ExtensionHelper(object):
    """
    Helper class for easy access of device extensions
    """
    @classmethod
    def get_device_modules(cls, use_cython: bool):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        include_dir = os.path.realpath(os.path.join(cur_dir, "includes"))
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
            lib_dir = os.path.realpath(os.path.join(cur_dir, "lib/win"))
            for dev_name, params in devices.items():
                result.append(cls.get_device_extension(dev_name, [params["lib"]], [lib_dir], [include_dir]))

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

        sys.path.append(os.path.realpath(os.path.join(cur_dir, "lib")))

        compiler = ccompiler.new_compiler()
        for dev_name, params in devices.items():
            if build_device_extensions[dev_name] == 0:
                print("\nSkipping native {0} support\n".format(dev_name))
                continue
            if build_device_extensions[dev_name] == 1:
                print("\nEnforcing native {0} support\n".format(dev_name))
                result.append(
                    cls.get_device_extension(dev_name, [params["lib"]], library_dirs, [include_dir], use_cython))
                continue

            if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                     include_dirs=[include_dir]):
                print("\nFound {0} lib. Will compile with native {1} support\n".format(params["lib"], dev_name))
                result.append(
                    cls.get_device_extension(dev_name, [params["lib"]], library_dirs, [include_dir], use_cython))
            elif dev_name in fallbacks:
                print("Trying fallback for {0}".format(dev_name))
                params = fallbacks[dev_name]
                dev_name += "_fallback"
                if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                         include_dirs=[include_dir]):
                    print("\nFound fallback. Will compile with native {0} support\n".format(dev_name))
                    result.append(
                        cls.get_device_extension(dev_name, [params["lib"]], library_dirs, [include_dir], use_cython))
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
