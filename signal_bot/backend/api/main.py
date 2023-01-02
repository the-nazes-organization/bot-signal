import logging
import logging.config

from fastapi import FastAPI

from signal_bot.backend.api.endpoints.v1.api import api_router as api_v1_router
from signal_bot.backend.core.config import get_settings
from signal_bot.backend.core.logger_conf import LOGGING

settings = get_settings()
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


logger.info("Starting the application")
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
