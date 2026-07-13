import logging
import sys

from app.config.settings import settings

logger = logging.getLogger("mall_agent")
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
)
logger.addHandler(handler)
