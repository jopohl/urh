import logging
import os
import sys
import tempfile

from urh.constants import color

LOG_LEVEL_PATH = os.path.join(tempfile.gettempdir(), "urh_log_level")


def read_log_level(default):
    try:
        with open(LOG_LEVEL_PATH, "r") as f:
            return int(f.readlines()[0].strip())
    except:
        return default


def save_log_level():
    try:
        with open(LOG_LEVEL_PATH, "w") as f:
            f.write(str(logger.level))
    except:
        pass


logger_conf = {
    "level": read_log_level(default=logging.DEBUG),
    "format": '[%(levelname)s::%(filename)s::%(funcName)s] %(message)s'
}

log_file_handler = None
if hasattr(sys, "frozen"):
    try:
        sys.stdin.isatty()
    except:
        # STDIN is not useable, so we are running in GUI mode
        logfile_name = os.path.join(tempfile.gettempdir(), "urh.log")
        # Add the log message handler to the logger
        import logging.handlers
        log_file_handler = logging.handlers.RotatingFileHandler(logfile_name, maxBytes=2e6, backupCount=5)

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

if log_file_handler is not None:
    logger.addHandler(log_file_handler)