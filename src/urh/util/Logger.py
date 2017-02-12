import logging
from urh.constants import color

logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')
logging.addLevelName(logging.WARNING, "{0}{1}{2}".format(color.YELLOW+color.BOLD, logging.getLevelName(logging.WARNING), color.END))
logging.addLevelName(logging.ERROR, "{0}{1}{2}".format(color.RED+color.BOLD, logging.getLevelName(logging.ERROR), color.END))
logging.addLevelName(logging.CRITICAL, "{0}{1}{2}".format(color.RED+color.BOLD, logging.getLevelName(logging.CRITICAL), color.END))

logger = logging.getLogger("urh")
logger.setLevel(logging.DEBUG)
