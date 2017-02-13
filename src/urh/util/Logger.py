import logging
from urh.constants import color

logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')

logging_colors_per_level = {
    logging.WARNING: color.YELLOW,
    logging.ERROR: color.RED,
    logging.CRITICAL: color.RED
}

for level, level_color in logging_colors_per_level.items():
    logging.addLevelName(level, "{0}{1}{2}".format(level_color+color.BOLD, logging.getLevelName(level), color.END))

logger = logging.getLogger("urh")
logger.setLevel(logging.DEBUG)
