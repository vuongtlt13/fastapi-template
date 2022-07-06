import logging
import sys

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'

LOGGER = logging.getLogger("app")
LOGGER.handlers = []
LOGGER.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(fmt=logging.Formatter(LOG_FORMAT))
LOGGER.addHandler(stream_handler)
