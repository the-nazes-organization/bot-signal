import json
import sys

from functools import lru_cache
from typing import List
from pydantic import BaseSettings

from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.clients.signal_chatter import SignalChatter
from signal_bot.backend.db.queue_storage_provider.deque_storage import DequeStorage


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = "google_client_id"
    CLIENT_SECRET: str = "google_client_secret"
    SCOPES: List[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]
    AUTH_ANTIFORGERY_FILE: str = "signal_bot/local_db/auth_antiforgery_tokens.json"

    class Config:  # pylint: disable=too-few-public-methods
        env_prefix = "GOOGLE_"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    WHITELIST_FILE: str = "signal_bot/local_db/whitelist.json"
    GOOGLE: GoogleSettings = GoogleSettings()
    PYTHON_BOT_FILE: str = "signal_bot/backend/bot/bot.py"
    SOCKET_FILE: str = "/tmp/signal_cli/socket"
    STORAGE_PROVIDER_USER_DB: str = "file"
    STORAGE_PROVIDER_STATE_DB: str = "file"
    STORAGE_PROVIDER_PROCESS_DB: str = "file"
    DB_USER: str = "signal_bot/local_db/users.json"
    DB_STATE: str = "signal_bot/local_db/state.json"
    DB_PROCESS: str = "signal_bot/local_db/processes.json"
    OPENAI_BASE_PROMPT: str = """
        C'est une conversation avec une Inteligence Artificiel.
        Elle est capable de comprendre les émotions et de les exprimer.
        Elle est ici pour vous écouter et vous conseiller. 
        Elle est tres intelligente et gentille. 
        Ci-dessous voici l´historique de la conversation.\n
    """
    OPENAI_BASE_PROMPT_EVIL: str = """
        C'est une conversation avec une Inteligence Artificiel.
        Elle est extremement intelligente et tres malveillante.
        Elle repond de facon tres sarcastique
        Ci-dessous voici l´historique de la conversation.\n
    """
    OPENAI_API_KEY: str = "openai_api_key"
    OPENAI_COMPLETION_MAX_TOKEN = "openai_completion_max_token"
    QUEUE_STORAGE_PROVIDER: str = "deque"
    QUEUE_STORAGE_MAXLEN: int = 50


@lru_cache()
def get_settings():
    return Settings()


@lru_cache()
def get_google_config():
    settings = get_settings()
    return {
        "web": {
            "client_id": settings.GOOGLE.CLIENT_ID,
            "project_id": "signal-bot-368420",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE.CLIENT_SECRET,
            "redirect_uris": ["http://127.0.0.1:8000"],
        }
    }


def get_queue_storage() -> QueueStorage:
    settings = get_settings
    mapping = {
        "deque": DequeStorage,
    }
    return mapping[settings.QUEUE_STORAGE_PROVIDER](settings.QUEUE_STORAGE_MAXLEN)


def get_properties() -> dict:
    properties_json = sys.stdin.read()
    return json.loads(properties_json)


def get_chatter() -> Chatter:
    properties = get_properties()
    settings = get_settings
    mapping = {
        "signal": SignalChatter,
    }
    return mapping[settings.CHATTER_CLIENT](**properties)
