import logging
import os

import sys
import tempfile

from urh.constants import color

logger_conf = {
    "level": logging.WARNING,
    "format": '[%(levelname)s::%(filename)s::%(funcName)s] %(message)s'
}

if hasattr(sys, "frozen"):
    logger_conf["filename"] = os.path.join(tempfile.gettempdir(), "urh.log")
    if sys.version_info >= (3, 5):
        logger_conf["filemode"] = "w"


logging.basicConfig(**logger_conf)

logging_colors_per_level = {
    logging.WARNING: color.YELLOW,
    logging.ERROR: color.RED,
    logging.CRITICAL: color.RED
}

for level, level_color in logging_colors_per_level.items():
    if sys.platform != "win32":
        logging.addLevelName(level, "{0}{1}{2}".format(level_color, logging.getLevelName(level), color.END))

logger = logging.getLogger("urh")
logger.setLevel(logging.DEBUG)
