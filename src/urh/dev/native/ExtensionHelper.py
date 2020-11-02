import os
import shutil
import sys
import tempfile
from collections import defaultdict
from distutils import ccompiler
from importlib import import_module
from subprocess import check_output

from setuptools import Extension

USE_RELATIVE_PATHS = False

COMPILER_DIRECTIVES = {'language_level': 3,
                       'cdivision': True,
                       'wraparound': False,
                       'boundscheck': False,
                       'initializedcheck': False,
                       }

DEVICES = {
    "airspy": {"lib": "airspy", "test_function": "open"},
    "bladerf": {"lib": "bladeRF", "test_function": "bladerf_open",
                "api_header_include": "libbladeRF.h",
                "api_version_check_code":
                    """
                    #include<stdio.h>
                    #include<libbladeRF.h>
                    
                    int main(void) {
                    struct bladerf_version result; bladerf_version(&result);
                    printf("%f", result.major + result.minor/10.0 + result.patch/100.0);
                    return 0;}
                    """},
    "hackrf": {"lib": "hackrf", "test_function": "hackrf_init",
               "extras": {"HACKRF_MULTI_DEVICE_SUPPORT": "hackrf_open_by_serial"}},
    "limesdr": {"lib": "LimeSuite", "test_function": "LMS_GetDeviceList"},
    "plutosdr": {"lib": "iio", "test_function": "iio_create_default_context"},
    "rtlsdr": {"lib": "rtlsdr", "test_function": "rtlsdr_get_device_name",
               "extras": {"RTLSDR_BANDWIDTH_SUPPORT": "rtlsdr_set_tuner_bandwidth"}},
    # Use C only for USRP to avoid boost dependency
    "usrp": {"lib": "uhd", "test_function": "uhd_usrp_find", "language": "c"},
    "sdrplay": {"lib": "mir_sdr_api" if sys.platform == "win32" else "mirsdrapi-rsp",
                "test_function": "mir_sdr_ApiVersion",
                "api_version_check_code":
                    """
                    #include<stdio.h>
                    int main(void) {
                    float version=0.0; mir_sdr_ApiVersion(&version); printf("%f", version); return 0;}
                    """}
}


def compiler_has_function(compiler, function_name, libraries, library_dirs, include_dirs) -> bool:
    tmp_dir = tempfile.mkdtemp(prefix='urh-')
    devnull = old_stderr = None
    try:
        try:
            file_name = os.path.join(tmp_dir, '{}.c'.format(function_name))
            with open(file_name, 'w') as f:
                # declare function in order to prevent Clang 12 error (https://github.com/jopohl/urh/issues/811)
                f.write('void %s();\n' % function_name)
                f.write('int main(void) {\n')
                f.write('    %s();\n' % function_name)
                f.write('}\n')

            # Redirect stderr to /dev/null to hide any error messages from the compiler.
            devnull = open(os.devnull, 'w')
            old_stderr = os.dup(sys.stderr.fileno())
            os.dup2(devnull.fileno(), sys.stderr.fileno())
            objects = compiler.compile([file_name], include_dirs=include_dirs)
            compiler.link_executable(objects, os.path.join(tmp_dir, "a.out"), library_dirs=library_dirs,
                                     libraries=libraries)
        except Exception as e:
            return False
        return True
    finally:
        if old_stderr is not None:
            os.dup2(old_stderr, sys.stderr.fileno())
        if devnull is not None:
            devnull.close()
        shutil.rmtree(tmp_dir)


def check_api_version(compiler, api_version_code, libraries, library_dirs, include_dirs) -> float:
    tmp_dir = tempfile.mkdtemp(prefix='urh-')
    devnull = old_stderr = None
    try:
        try:
            file_name = os.path.join(tmp_dir, 'get_api_version.c')
            with open(file_name, 'w') as f:
                f.write(api_version_code)

            # Redirect stderr to /dev/null to hide any error messages from the compiler.
            devnull = open(os.devnull, 'w')
            old_stderr = os.dup(sys.stderr.fileno())
            os.dup2(devnull.fileno(), sys.stderr.fileno())
            objects = compiler.compile([file_name], include_dirs=include_dirs)
            check_api_program = os.path.join(tmp_dir, "check_api")
            compiler.link_executable(objects, check_api_program, library_dirs=library_dirs, libraries=libraries)

            env = os.environ.copy()
            env["PATH"] = os.pathsep.join(library_dirs) + os.pathsep + os.environ.get("PATH", "")
            if sys.platform == "darwin":
                for path in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
                    ld_path = os.pathsep.join(library_dirs) + os.pathsep + os.environ.get(path, "")
                    env[path] = ld_path

            result = float(check_output(check_api_program, env=env))
            print("    Automatic API version check succeeded.")
            return result
        except Exception as e:
            print("    API version check failed: {}".format(e))
            return 0.0
    finally:
        if old_stderr is not None:
            os.dup2(old_stderr, sys.stderr.fileno())
        if devnull is not None:
            devnull.close()
        shutil.rmtree(tmp_dir)


def get_device_extensions_and_extras(library_dirs=None, include_dirs=None):
    library_dirs = [] if library_dirs is None else library_dirs

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    include_dirs = [] if include_dirs is None else include_dirs

    device_extras = dict()

    if os.path.isdir(os.path.join(cur_dir, "lib/shared")):
        # Device libs are packaged, so we are in release mode
        include_dirs.insert(0, os.path.realpath(os.path.join(cur_dir, "lib/shared/include")))
        library_dirs.insert(0, os.path.realpath(os.path.join(cur_dir, "lib/shared")))

    if sys.platform == "darwin":
        # On Mac OS X clang is by default not smart enough to search in the lib dir
        # see: https://github.com/jopohl/urh/issues/173
        if os.path.isdir("/opt/local/lib"):
            library_dirs.append("/opt/local/lib")
        library_dirs.append("/usr/local/lib")
        if os.path.isdir("/opt/local/include"):
            include_dirs.append("/opt/local/include")

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
        elif compiler_has_function(compiler, params["test_function"], (params["lib"],), library_dirs, include_dirs):
            print("Found {0} lib. Will compile with native {1} support".format(params["lib"], dev_name))
        else:
            print("Skipping native support for {0}".format(dev_name))
            continue

        device_extras.update(get_device_extras(compiler, dev_name, [params["lib"]], library_dirs, include_dirs))
        if "api_version_check_code" in params:
            env_name = dev_name.upper() + "_API_VERSION"
            ver = os.getenv(env_name)
            if ver is not None:
                try:
                    ver = float(ver)
                except Exception as e:
                    print("    Could not convert content of {} to float: {}".format(env_name, e))
                    print("    Will now try to automatically detect API version.")
                    ver = None
            else:
                print("    Environment variable {} is unset, try to automatically detect API version".format(env_name))

            if ver is None:
                ver = check_api_version(compiler, params["api_version_check_code"], (params["lib"],),
                                        library_dirs, include_dirs)
            device_extras[env_name] = ver
            print("    Using {}={}".format(env_name, ver))

        extension = get_device_extension(dev_name, [params["lib"]], library_dirs, include_dirs)
        result.append(extension)

    return result, device_extras


def get_device_extras(compiler, dev_name, libraries, library_dirs, include_dirs):
    try:
        extras = DEVICES[dev_name]["extras"]
    except KeyError:
        extras = dict()

    result = dict()

    for extra, func_name in extras.items():
        if compiler_has_function(compiler, func_name, libraries, library_dirs, include_dirs):
            result[extra] = 1
        else:
            print("Skipping {} as installed driver does not support it".format(extra))
            result[extra] = 0

    return result


def get_device_extension(dev_name: str, libraries: list, library_dirs: list, include_dirs: list):
    try:
        language = DEVICES[dev_name]["language"]
    except KeyError:
        language = "c++"

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    if USE_RELATIVE_PATHS:
        # We need relative paths on windows
        cpp_file_path = "src/urh/dev/native/lib/{0}.pyx".format(dev_name)
    else:
        cpp_file_path = os.path.join(cur_dir, "lib", "{0}.pyx".format(dev_name))

    return Extension("urh.dev.native.lib." + dev_name,
                     [cpp_file_path],
                     libraries=libraries, library_dirs=library_dirs,
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
        library_directories = sys.argv[sys.argv.index("-L") + 1].split(":")
    else:
        library_directories = None

    if "-I" in sys.argv:
        include_directories = sys.argv[sys.argv.index("-I") + 1].split(":")
    else:
        include_directories = []

    import numpy as np

    include_directories.append(np.get_include())

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(os.path.join(cur_dir, "..", "..", ".."))

    try:
        from Cython.Build import cythonize
    except ImportError:
        print("You need Cython to rebuild URH's device extensions. "
              "You can get it e.g. with python3 -m pip install cython.",
              file=sys.stderr)
        sys.exit(1)

    dev_extensions, dev_extras = get_device_extensions_and_extras(library_dirs=library_directories,
                                                                  include_dirs=include_directories)
    setup(
        name="urh",
        ext_modules=cythonize(dev_extensions, force=True,
                              compile_time_env=dev_extras, compiler_directives=COMPILER_DIRECTIVES,
                              )
    )
