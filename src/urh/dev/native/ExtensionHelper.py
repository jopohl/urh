import os

import sys
import platform
import tempfile
from collections import defaultdict
from distutils import ccompiler

import pickle
from setuptools import Extension


USE_RELATIVE_PATHS = False

DEVICES = {
    "airspy": {"lib": "airspy", "test_function": "open"},
    "hackrf": {"lib": "hackrf", "test_function": "hackrf_init"},
    "limesdr": {"lib": "LimeSuite", "test_function": "LMS_GetDeviceList"},
    "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_set_tuner_bandwidth"},
    # Use C only for USRP to avoid boost dependency
    "usrp": {"lib": "uhd", "test_function": "uhd_usrp_find", "language": "c"},
}

FALLBACKS = {
    "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_get_device_name"}
}


def get_device_extensions(use_cython: bool, library_dirs=None):
    library_dirs = [] if library_dirs is None else library_dirs

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    include_dirs = [os.path.realpath(os.path.join(cur_dir, "includes"))]

    if sys.platform == "win32":
        if platform.architecture()[0] != "64bit":
            return []  # only 64 bit python supported for native device backends

        result = []
        lib_dir = os.path.realpath(os.path.join(cur_dir, "lib/win/x64"))
        for dev_name, params in DEVICES.items():
            result.append(get_device_extension(dev_name, [params["lib"]], [lib_dir], include_dirs))

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

    for dev_name in DEVICES:
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
    for dev_name, params in DEVICES.items():
        if build_device_extensions[dev_name] == 0:
            print("\nSkipping native {0} support\n".format(dev_name))
            continue
        if build_device_extensions[dev_name] == 1:
            print("\nEnforcing native {0} support\n".format(dev_name))
            result.append(
                get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, use_cython))
            continue

        if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                 include_dirs=include_dirs):
            print("\nFound {0} lib. Will compile with native {1} support\n".format(params["lib"], dev_name))
            result.append(
                get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, use_cython))
        elif dev_name in FALLBACKS:
            print("Trying fallback for {0}".format(dev_name))
            params = FALLBACKS[dev_name]
            dev_name += "_fallback"
            if compiler.has_function(params["test_function"], libraries=(params["lib"],), library_dirs=library_dirs,
                                     include_dirs=include_dirs):
                print("\nFound fallback. Will compile with native {0} support\n".format(dev_name))
                result.append(
                    get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, use_cython))
        else:
            print("\nSkipping native support for {1}\n".format(params["lib"], dev_name))

        # remove Temp file for checking
        try:
            os.remove("a.out")
        except OSError:
            pass

        for filename in os.listdir(tempfile.gettempdir()):
            dev_name = dev_name.replace("_fallback", "")
            func_names = [DEVICES[dev_name]["test_function"]]
            if dev_name in FALLBACKS:
                func_names.append(FALLBACKS[dev_name]["test_function"])

            if any(filename.startswith(func_name) for func_name in func_names) and filename.endswith(".c"):
                os.remove(os.path.join(tempfile.gettempdir(), filename))

    return result


def get_device_extension(dev_name: str, libraries: list, library_dirs: list, include_dirs: list, use_cython=False):
    try:
        language = DEVICES[dev_name]["language"]
    except KeyError:
        language = "c++"

    file_ext = "pyx" if use_cython else "cpp" if language == "c++" else "c"
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    if USE_RELATIVE_PATHS:
        # We need relative paths on windows
        cpp_file_path = "src/urh/dev/native/lib/{0}.{1}".format(dev_name, file_ext)
    else:
        cpp_file_path = os.path.join(cur_dir, "lib", "{0}.{1}".format(dev_name, file_ext))

    return Extension("urh.dev.native.lib." + dev_name,
                     [cpp_file_path],
                     libraries=libraries, library_dirs=library_dirs,
                     include_dirs=include_dirs, language=language)


if __name__ == "__main__":
    from setuptools import setup

    extensions = pickle.load(open(os.path.join(tempfile.gettempdir(), "native_extensions"), "rb"))
    assert isinstance(extensions, list)

    setup(
        name="urh",
        ext_modules=extensions,
    )
