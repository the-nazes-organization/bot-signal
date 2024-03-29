import os

from app.config import get_settings

settings = get_settings()

if not os.path.exists(os.path.join(settings.LOGS_PATH)):
    os.makedirs(os.path.join(settings.LOGS_PATH))


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": settings.LOG_LEVEL_CONSOLE,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file_cli": {
            "level": settings.LOG_LEVEL_CLI,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(settings.VOLUME_PATH, "logs", "signal_cli.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 2,
            "encoding": "utf8",
        },
        "file_bot": {
            "level": settings.LOG_LEVEL_BOT,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(settings.VOLUME_PATH, "logs", "bot.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 2,
            "encoding": "utf8",
        },
        "file_uvicorn": {
            "level": settings.LOG_LEVEL_UVICORN,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(settings.VOLUME_PATH, "logs", "uvicorn.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 2,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "app.backend.core.process_handler": {
            "handlers": ["console", "file_cli"],
            "level": "DEBUG",
            "propagate": True,
        },
        "app.backend.api": {
            "handlers": ["console", ],
            "level": "DEBUG",
            "propagate": True,
        },
        "app.bot": {
            "handlers": ["console", "file_bot"],
            "level": "DEBUG",
            "propagate": True,
        },
        "app.commands": {
            "handlers": ["console", "file_cli"],
            "level": "DEBUG",
            "propagate": True,
        },
        "uvicorn": {
            "handlers": ["console", "file_uvicorn"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
