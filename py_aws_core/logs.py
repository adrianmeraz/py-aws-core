import logging
import os
import sys

import structlog
from dotenv import load_dotenv

dotenv = load_dotenv()  # take environment variables from .env.
level = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, level)

exception_transformer = structlog.processors.ExceptionDictTransformer(locals_max_length=10000, locals_max_string=10000)

shared_processors = [
    structlog.processors.EventRenamer('message'),
    structlog.processors.CallsiteParameterAdder(),
    structlog.processors.TimeStamper(fmt='iso'),
    structlog.processors.add_log_level,
    structlog.processors.ExceptionPrettyPrinter(exception_formatter=exception_transformer),
]
val = sys.stderr.isatty()
if 'unittest' in sys.modules or sys.stderr.isatty():
    # Pretty printing when we run tests or a terminal session.
    # Automatically prints pretty tracebacks when "rich" is installed
    processors = shared_processors + [
        structlog.dev.ConsoleRenderer(
            colors=True,
            event_key='message'
        ),
    ]
else:
    # Print JSON when we run, e.g., in a Docker container.
    # Also print structured tracebacks.
    processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]
structlog.configure(
    processors=processors,
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL)
)

__logger = structlog.get_logger(__name__)


def get_logger():
    return __logger
