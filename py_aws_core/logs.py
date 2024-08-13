import logging.config
import os

from dotenv import load_dotenv

dotenv = load_dotenv()  # take environment variables from .env.

logger = logging.getLogger(__name__)


class Logging:
    @classmethod
    def get_logging_config(cls) -> dict:
        return {
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
                    'level': cls.get_log_level(),
                    'propagate': True,
                }
            },
        }

    @classmethod
    def get_log_level(cls):
        log_level_upper = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
        return getattr(logging, log_level_upper)

    @classmethod
    def configure_logger(cls):
        logging.config.dictConfig(Logging.get_logging_config())


Logging.configure_logger()
