import fileinput
import os
import shutil
import sys
import tempfile
from subprocess import call, check_output


def cleanup():
    """
    Remove all cache directories
    :return:
    """
    script_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
    script_dir = os.path.realpath(os.path.join(script_dir, ".."))
    shutil.rmtree(os.path.join(script_dir, "dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(script_dir, "tmp"), ignore_errors=True)
    shutil.rmtree(os.path.join(script_dir, "urh.egg-info"), ignore_errors=True)
    shutil.rmtree(os.path.join(script_dir, "src", "urh.egg-info"), ignore_errors=True)
    shutil.rmtree(os.path.join(script_dir, "src", "urh", "tmp"), ignore_errors=True)


def release():
    script_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(os.readlink(__file__))
    script_dir = os.path.realpath(os.path.join(script_dir, ".."))
    os.chdir(script_dir)

    current_branch = check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("UTF-8").strip()

    # if current_branch != "master":
    #     print("You can only release from master!")
    #     sys.exit(1)

    open(os.path.join(tempfile.gettempdir(), "urh_releasing"), "w").close()

    from src.urh import version
    version_file = os.path.realpath(os.path.join(script_dir, "src", "urh", "version.py"))

    cur_version = version.VERSION
    numbers = cur_version.split(".")
    numbers[-1] = str(int(numbers[-1]) + 1)
    cur_version = ".".join(numbers)

    with open(version_file, "w") as f:
        f.write('VERSION = "{0}" \n'.format(cur_version))

    desktop_file = os.path.realpath(os.path.join(script_dir, "urh.desktop"))
    for line in fileinput.input(desktop_file, inplace=True):
        if line.startswith("Version="):
            print("Version=" + cur_version)
        else:
            print(line, end="")

    # Publish new version number
    call(["git", "add", version_file, desktop_file])
    call(["git", "commit", "-m", "version" + cur_version])
    call(["git", "push"])

    # Publish to PyPi
    os.chdir(script_dir)

    # Remove local tags
    call("git tag -l | xargs git tag -d", shell=True)
    call(["git", "fetch", "--tags"])

    call(["git", "tag", "v" + cur_version, "-m", "version " + cur_version])
    call(["git", "push", "origin", "--tags"])  # Creates tar package on https://github.com/jopohl/urh/tarball/va.b.c.d
    call(["python", "setup.py", "register", "-r", "pypi"])
    call(["python", "setup.py", "sdist", "upload", "-r", "pypi"])

    # Publish to AUR
    # Adapt pkgver
    # Regenerate md5sum and sha256sum
    os.chdir(tempfile.gettempdir())
    call(["wget", "https://github.com/jopohl/urh/tarball/v" + cur_version])
    md5sum = check_output(["md5sum", "v" + cur_version]).decode("ascii").split(" ")[0]
    sha256sum = check_output(["sha256sum", "v" + cur_version]).decode("ascii").split(" ")[0]
    print("md5sum", md5sum)
    print("sha256sum", sha256sum)

    shutil.rmtree("aur", ignore_errors=True)
    os.mkdir("aur")
    os.chdir("aur")
    call(["git", "clone", "git+ssh://aur@aur.archlinux.org/urh.git"])
    try:
        os.chdir("urh")
    except FileNotFoundError:
        input("Could not clone AUR package. Please clone manually in {}".format(os.path.realpath(os.curdir)))
        os.chdir("urh")

    for line in fileinput.input("PKGBUILD", inplace=True):
        if line.startswith("pkgver="):
            print("pkgver=" + cur_version)
        elif line.startswith("md5sums="):
            print("md5sums=('" + md5sum + "')")
        elif line.startswith("sha256sums="):
            print("sha256sums=('" + sha256sum + "')")
        else:
            print(line, end="")

    call("makepkg --printsrcinfo > .SRCINFO", shell=True)
    call(["git", "commit", "-am", "version " + cur_version])
    call(["git", "push"])

    os.remove(os.path.join(tempfile.gettempdir(), "urh_releasing"))


if __name__ == "__main__":
    cleanup()
    release()
    cleanup()
