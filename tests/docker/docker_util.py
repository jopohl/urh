from urh.util.Logger import logger
from subprocess import check_output, call
import os, sys

USE_SUDO = True
SUPPORTED_IMAGES = ("archlinux", "centos7", "debian8", "ubuntu1404", "ubuntu1604", "kali")

def is_image_there(imagename: str) -> bool:
    cmd = ["sudo"] if USE_SUDO else []
    cmd.extend(["docker", "images", "-q", "urh/" + imagename])
    return len(check_output(cmd)) > 0

def build_image(imagename: str):
    if imagename not in SUPPORTED_IMAGES:
        logger.error("{} is not a supported docker image".format(imagename))
        sys.exit(1)

    cmd = ["sudo"] if USE_SUDO else []
    cmd.extend(["docker", "build", "--force-rm", "--no-cache",
                "--tag", "urh/"+imagename, "-f", imagename, "."])

    print(" ".join(cmd))

    script = __file__ if not os.path.islink(__file__) else os.readlink(__file__)
    os.chdir(os.path.realpath(os.path.join(script, "..")))

    call(cmd)

def run_image(imagename: str, rebuild=False):
    if not is_image_there(imagename) or rebuild:
        build_image(imagename)

    cmd = ["sudo"] if USE_SUDO else []
    call(cmd + ["xhost", "+"]) # Allow docker to connect to hosts X Server

    cmd.extend(["docker", "run", "-e", "DISPLAY=$DISPLAY", "-v", "/tmp/.X11-unix:/tmp/.X11-unix", "urh/"+imagename])
    logger.info("call {}".format(" ".join(cmd)))
    rc = call(" ".join(cmd), shell=True)
    return rc == 0

def remove_containers():
    logger.info("removing containers")
    cmd = ["sudo"] if USE_SUDO else []
    cmd.extend(["docker", "rm", "-f", "$({}docker ps -aq)".format("sudo " if USE_SUDO else "")])
    call(" ".join(cmd), shell=True)

if __name__ == "__main__":
    run_image("archlinux")
