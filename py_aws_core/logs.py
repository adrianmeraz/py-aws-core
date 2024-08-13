import logging.config
import os

logger = logging.getLogger(__name__)

log_level_upper = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logger.info(f'LOG_LEVEL: {log_level_upper}')
LOG_LEVEL = getattr(logging, log_level_upper)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
        'verbose': {
            'format': '[{asctime} {levelname}/{threadName}] {message}',
            'style': '{',
        },
        'verbose_plus': {
            'format': '[{asctime} {levelname}/{threadName} {pathname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
