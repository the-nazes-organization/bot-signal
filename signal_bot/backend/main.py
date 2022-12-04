import logging
import sys

from fastapi import FastAPI

from signal_bot.backend.api.v1.api import api_router
from signal_bot.backend.core.config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router, prefix=settings.API_V1_STR)
