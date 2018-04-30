import os
import platform
import sys
import tempfile
from collections import defaultdict
from distutils import ccompiler
from importlib import import_module

import shutil
from setuptools import Extension

USE_RELATIVE_PATHS = False

DEVICES = {
    "airspy": {"lib": "airspy", "test_function": "open"},
    "hackrf": {"lib": "hackrf", "test_function": "hackrf_init",
               "extras": {"HACKRF_MULTI_DEVICE": "hackrf_open_by_serial"}},
    "limesdr": {"lib": "LimeSuite", "test_function": "LMS_GetDeviceList"},
    "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_get_device_name",
               "extras": {"RTLSDR_BANDWIDTH": "rtlsdr_set_tuner_bandwidth"}},
    # Use C only for USRP to avoid boost dependency
    "usrp": {"lib": "uhd", "test_function": "uhd_usrp_find", "language": "c"},
    "sdrplay": {"lib": "mir_sdr_api" if sys.platform == "win32" else "mirsdrapi-rsp",
                "test_function": "mir_sdr_ApiVersion"}
}


def compiler_has_function(compiler, function_name, libraries, library_dirs, include_dirs) -> bool:
    tmp_dir = tempfile.mkdtemp(prefix='urh-')
    devnull = old_stderr = None
    try:
        try:
            file_name = os.path.join(tmp_dir, '{}.c'.format(function_name))
            f = open(file_name, 'w')
            f.write('int main(void) {\n')
            f.write('    %s();\n' % function_name)
            f.write('}\n')
            f.close()
            # Redirect stderr to /dev/null to hide any error messages from the compiler.
            devnull = open(os.devnull, 'w')
            old_stderr = os.dup(sys.stderr.fileno())
            os.dup2(devnull.fileno(), sys.stderr.fileno())
            objects = compiler.compile([file_name], include_dirs=include_dirs)
            compiler.link_executable(objects, os.path.join(tmp_dir, "a.out"), library_dirs=library_dirs, libraries=libraries)
        except Exception as e:
            return False
        return True
    finally:
        if old_stderr is not None:
            os.dup2(old_stderr, sys.stderr.fileno())
        if devnull is not None:
            devnull.close()
        shutil.rmtree(tmp_dir)


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
            # Since windows drivers are bundled we can enforce the macros
            macros = [(extra, None) for extra in params.get("extras", dict())]
            result.append(get_device_extension(dev_name, [params["lib"]], [lib_dir], include_dirs, macros))

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
            print("Skipping native {0} support".format(dev_name))
            continue
        if build_device_extensions[dev_name] == 1:
            print("Enforcing native {0} support".format(dev_name))
            macros = __get_device_extra_macros(compiler, dev_name, [params["lib"]], library_dirs, include_dirs)
            extension = get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, macros, use_cython)
            result.append(extension)
            continue

        if compiler_has_function(compiler, params["test_function"], (params["lib"],), library_dirs, include_dirs):
            print("Found {0} lib. Will compile with native {1} support".format(params["lib"], dev_name))
            macros = __get_device_extra_macros(compiler, dev_name, [params["lib"]], library_dirs, include_dirs)
            extension = get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs, macros, use_cython)
            result.append(extension)
        else:
            print("Skipping native support for {1}".format(params["lib"], dev_name))

    return result


def __get_device_extra_macros(compiler, dev_name, libraries, library_dirs, include_dirs):
    try:
        extras = DEVICES[dev_name]["extras"]
    except KeyError:
        extras = dict()

    macros = []

    for extra, func_name in extras.items():
        if compiler_has_function(compiler, func_name, libraries, library_dirs, include_dirs):
            macros.append((extra, None))
        else:
            print("Skipping {} as installed driver does not support it".format(extra))

    return macros

def get_device_extension(dev_name: str, libraries: list, library_dirs: list, include_dirs: list, macros: list,
                         use_cython=False):
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
                     define_macros=macros,
                     include_dirs=include_dirs, language=language)


def perform_health_check() -> str:
    result = []
    for device in sorted(DEVICES.keys()):
        try:
            _ = import_module("urh.dev.native.lib." + device)
            result.append(device + " -- OK")
        except ImportError as e:
            result.append(device + " -- ERROR: " + str(e))

    return "\n".join(result)


if __name__ == "__main__":
    from setuptools import setup
    if "-L" in sys.argv:
        library_dirs = sys.argv[sys.argv.index("-L")+1].split(":")
    else:
        library_dirs = None

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir("..")

    setup(
        name="urh",
        ext_modules=get_device_extensions(use_cython=False, library_dirs=library_dirs),
    )
