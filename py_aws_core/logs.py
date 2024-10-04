import logging
import os

import structlog
from dotenv import load_dotenv


dotenv = load_dotenv()  # take environment variables from .env.
level = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, level)
structlog.configure(
    processors=[
        structlog.processors.EventRenamer("message"),
        structlog.processors.CallsiteParameterAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL)
)

__logger = structlog.get_logger(__name__)


def get_logger():
    return __logger
