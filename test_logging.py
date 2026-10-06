import logging

from parser.logging_config import configure_logging


configure_logging()

logger = logging.getLogger("TestLogger")

logger.info("Logging test successful.")
logger.warning("This is a warning test.")
logger.error("This is an error test.")