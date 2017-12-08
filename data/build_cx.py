import os
import sys

import cx_Freeze

def build_exe(build_cmd='build'):
    # have to make sure args looks right
    sys.argv = sys.argv[:1] + [build_cmd]

    root_path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(root_path)

    app_path = os.path.join("src", "urh", "main.py")
    assert os.path.isfile(app_path)
    src_dir = os.path.join(os.curdir, "src")
    assert os.path.isdir(src_dir)
    sys.path.insert(0, src_dir)

    import urh.version as version

    if sys.platform == 'win32':
        include_files = [os.path.join("data", 'icons', 'appicon.ico')]
        arch = "x64" if sys.maxsize > 2 ** 32 else "x86"
        lib_path = os.path.join("src", "urh", "dev", "native", "lib", "win", arch)
        for f in os.listdir(lib_path):
            include_files.append(os.path.join(lib_path, f))

        executables = [cx_Freeze.Executable(
            app_path,
            targetName="urh.exe",
            icon=os.path.join("data", 'icons', 'appicon.ico'),
            shortcutName="Universal Radio Hacker",
            shortcutDir="DesktopFolder",
            base="Win32GUI")]
    else:
        include_files = [os.path.join("data", 'icons', 'appicon.png')]
        executables = [cx_Freeze.Executable(
            app_path,
            targetName="urh",
            icon=os.path.join("data", 'icons', 'appicon.png'))]

    for f in os.listdir(os.path.join("src", "urh", "dev", "gr", "scripts")):
        if f.endswith(".py"):
            include_files.append(os.path.join("src", "urh", "dev", "gr", "scripts", f))

    plugins = []
    plugin_path = os.path.join("src", "urh", "plugins")
    for plugin in os.listdir(plugin_path):
        if os.path.isdir(os.path.join(plugin_path, plugin)):
            for f in os.listdir(os.path.join(plugin_path, plugin)):
                if f.endswith(".py") and f != "__init__.py":
                    plugins.append("urh.plugins.{0}.{1}".format(plugin, f.replace(".py", "")))

    options = {
        'build_exe': {
            "include_files": include_files,
            "include_msvcr": True,
            "excludes": ["tkinter"],
            "includes": ['numpy.core._methods', 'numpy.lib.format', 'six', 'appdirs',
                         'packaging', 'packaging.version', 'packaging.specifiers', 'packaging.requirements',
                         'setuptools.msvc'] + plugins
        },
        'bdist_msi': {
            "upgrade_code": "{96abcdef-1337-4711-cafe-beef4a1ce42}"
        }
    }

    cx_Freeze.setup(
        name="Universal Radio Hacker",
        description="Universal Radio Hacker: investigate wireless protocols like a boss",
        author="Johannes Pohl",
        author_email="Johannes.Pohl90@gmail.com",
        url="https://github.com/jopohl/urh",
        license="GNU General Public License (GPL) 3",
        version=version.VERSION,
        executables=executables,
        options=options
    )


if __name__ == '__main__':
    if sys.platform == "win32":
        build_exe("bdist_msi")
    else:
        build_exe()
