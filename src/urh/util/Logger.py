import logging

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(message)s')
logging.addLevelName(logging.WARNING, "{0}{1}{2}".format(color.YELLOW+color.BOLD, logging.getLevelName(logging.WARNING), color.END))
logging.addLevelName(logging.ERROR, "{0}{1}{2}".format(color.RED+color.BOLD, logging.getLevelName(logging.ERROR), color.END))
logging.addLevelName(logging.CRITICAL, "{0}{1}{2}".format(color.RED+color.BOLD, logging.getLevelName(logging.CRITICAL), color.END))

logger = logging.getLogger("urh")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(' [%(levelname)s] %(message)s')


# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)