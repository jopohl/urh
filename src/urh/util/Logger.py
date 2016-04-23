import logging
import io
log_capture_string = io.StringIO()


logger = logging.getLogger("urh")
#logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

sh = logging.StreamHandler(log_capture_string)
sh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(' [%(levelname)s] %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(sh)