from urh.util.Logger import logger
from subprocess import check_output, call
import os, sys

USE_SUDO = True
SUPPORTED_IMAGES = ("archlinux", "centos7", "debian8", "ubuntu1404")

def is_image_there(imagename: str) -> bool:
    cmd = ["sudo"] if USE_SUDO else []
    cmd.extend(["docker", "images", "-q", "urh/" + imagename])
    return len(check_output(cmd)) > 0

def build_image(imagename: str):
    if imagename not in SUPPORTED_IMAGES:
        logger.error("{} is not a supported docker image".format(imagename))
        sys.exit(1)

    cmd = ["sudo"] if USE_SUDO else []
    cmd.extend(["docker", "build", "--tag", "urh/"+imagename, "-f", imagename, "."])

    script = __file__ if not os.path.islink(__file__) else os.readlink(__file__)
    os.chdir(os.path.realpath(os.path.join(script, "..")))

    call(cmd)

def run_image(imagename: str):
    if not is_image_there(imagename):
        logger.info("Could not find {} image. I will build it now.".format(imagename))
        build_image(imagename)

    cmd = ["sudo"] if USE_SUDO else []
    cmd.extend(["docker", "run", "-e", "DISPLAY=$DISPLAY", "-v", "/tmp/.X11-unix:/tmp/.X11-unix", "urh/"+imagename])
    rc = call(cmd)
    return rc == 0

if __name__ == "__main__":
    run_image("archlinux")
