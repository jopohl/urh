import logging

import sys

from urh.constants import color

logging.basicConfig(level=logging.WARNING, format='[%(levelname)s::%(filename)s::%(funcName)s] %(message)s')

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
