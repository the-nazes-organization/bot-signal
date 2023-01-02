import json
import sys

from functools import lru_cache
from typing import List
from pydantic import BaseSettings

from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.clients.signal_chatter import SignalChatter
from signal_bot.backend.bot.chat_client.clients.facebook_chatter import FacebookChatter
from signal_bot.backend.db.queue_storage_provider.deque_storage import DequeStorage
from signal_bot.backend.bot.chat_client.format_message import MessageFormater
from signal_bot.backend.bot.chat_client.format_message import JsonRpcFormater


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = "google_client_id"
    CLIENT_SECRET: str = "google_client_secret"
    SCOPES: List[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]

    class Config:  # pylint: disable=too-few-public-methods
        env_prefix = "GOOGLE_"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    GOOGLE: GoogleSettings = GoogleSettings()

    VOLUME_PATH: str = "volume_path"

    SIGNAL_CLI_CONFIG_DIR: str = "signal-cli_config"
    CHATTER_CLIENT: str = "signal"
    SOCKET_FILE: str = "/tmp/signal-cli/socket"
    PYTHON_BOT_FILE: str = "signal_bot/backend/bot/bot.py"

    STORAGE_PROVIDER_USER_DB: str = "file"
    STORAGE_PROVIDER_STATE_DB: str = "file"
    STORAGE_PROVIDER_PROCESS_DB: str = "file"
    STORAGE_PROVIDER_NUMBER_MAP_DB: str = "file"
    DB_USER: str = "db/users.json"
    DB_STATE: str = "db/state.json"
    DB_PROCESS: str = "db/processes.json"
    DB_NUMBER_MAP: str = "db/numbers_map.json"

    OPENAI_BASE_PROMPT: str = """
C'est une conversation avec une Inteligence Artificiel.\n
Elle est capable de comprendre les émotions et de les exprimer.\n
Elle est ici pour vous écouter et vous conseiller.\n
Elle est tres intelligente et gentille.\n 
Ci-dessous voici l´historique de la conversation.\n
La reponse est seulement le texte de la reponse de l´IA. Pas de prompt.\n
    """
    OPENAI_BASE_PROMPT_EVIL: str = """
C'est une conversation avec une Inteligence Artificiel.\n
Elle est extremement intelligente et tres malveillante.\n
Elle repond de facon tres sarcastique\n
Ci-dessous voici l´historique de la conversation.\n
La reponse est seulement le texte de la reponse de l´IA. Pas de prompt.\n
    """
    OPENAI_API_KEY: str = "openai_api_key"
    OPENAI_COMPLETION_MAX_TOKEN = "openai_completion_max_token"
    QUEUE_STORAGE_PROVIDER: str = "deque"
    QUEUE_STORAGE_MAXLEN: int = 50
    NUMBER_FORMAT_REGEX: str = r"^\+[0-9]{7,15}$"


@lru_cache()
def get_settings():
    return Settings()


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
            "redirect_uris": [
                "http://127.0.0.1:8000/api/v1/auth/callback",
                "http://signal-bot.nazes.fr/api/v1/auth/callback"
            ],
        }
    }

@lru_cache()
def get_signal_cli_config_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.SIGNAL_CLI_CONFIG_DIR

@lru_cache()
def get_db_user_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.DB_USER

@lru_cache()
def get_db_state_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.DB_STATE

@lru_cache()
def get_db_process_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.DB_PROCESS

@lru_cache()
def get_db_number_map_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.DB_NUMBER_MAP

def get_queue_storage() -> QueueStorage:
    settings = get_settings()
    mapping = {
        "deque": DequeStorage,
    }
    return mapping[settings.QUEUE_STORAGE_PROVIDER](settings.QUEUE_STORAGE_MAXLEN)


def get_formater(properties) -> MessageFormater:
    return JsonRpcFormater(**properties)


def get_properties() -> dict:
    properties_json = sys.stdin.read()
    sys.stdout.write(properties_json)
    return json.loads(properties_json)


def get_chatter(queue) -> Chatter:
    properties = get_properties()
    settings = get_settings()
    mapping = {
        "signal": SignalChatter,
        "facebook": FacebookChatter,
    }
    formater = get_formater(properties)
    return mapping[settings.CHATTER_CLIENT](
        queue=queue, formater=formater, socket_file=settings.SOCKET_FILE
    )
