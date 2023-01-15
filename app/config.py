import mimetypes
from base64 import b64encode
from functools import lru_cache
from typing import List

from pydantic import BaseSettings

from app.bot.chat_client.chatter import Chatter
from app.bot.chat_client.clients.facebook_chatter import FacebookChatter
from app.bot.chat_client.clients.signal.formater import MessageFormater
from app.bot.chat_client.clients.signal.formaters.jsonrpc import JsonRpcFormater
from app.bot.chat_client.clients.signal.signal_chatter import SignalChatter
from app.db.object_storage import ObjectStorage
from app.db.object_storage_provider.fs_storage import FsStorage
from app.db.object_storage_provider.json_storage import JsonStorage
from app.db.object_storage_provider.memory_storage import MemoryStorage
from app.db.queue_storage import QueueStorage
from app.db.queue_storage_provider.deque_storage import DequeStorage


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = "google_client_id"
    CLIENT_SECRET: str = "google_client_secret"
    SCOPES: List[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]

    class Config:
        env_prefix = "GOOGLE_"


class Settings(BaseSettings):
    ALLOW_EXECUTE_SELF_SEND: str = "n"
    API_V1_STR: str = "/api/v1"
    CHATTER_CLIENT: str = "signal"
    DB_NUMBER_MAP: str = "db/numbers_map.json"
    DB_PROCESS: str = "db/processes.json"
    DB_STATE: str = "db/state.json"
    DB_USER: str = "db/users.json"
    GOOGLE: GoogleSettings = GoogleSettings()
    LOGS_PATH: str = "/tmp/signal-bot/logs"
    LOG_LEVEL_BOT: str = "INFO"
    LOG_LEVEL_CLI: str = "INFO"
    LOG_LEVEL_CONSOLE: str = "DEBUG"
    LOG_LEVEL_UVICORN: str = "INFO"
    NUMBER_FORMAT_REGEX: str = r"^\+[0-9]{7,15}$"
    OPENAI_API_KEY: str = "openai_api_key"
    OPENAI_BASE_PROMPT_EVIL_PATH: str = "prompt/evil_ai.txt"
    OPENAI_BASE_PROMPT_PATH: str = "prompt/ignorant_ai.txt"
    OPENAI_COMPLETION_MAX_TOKEN = "1000"
    OPENAI_HISTORY_LENGTH: int = "20"
    PROJECT_NAME: str = "Signal Bot"
    PYTHON_BOT_FILE: str = "app/bot/bot.py"
    QUEUE_STORAGE_MAXLEN: int = 50
    QUEUE_STORAGE_PROVIDER: str = "deque"
    SIGNAL_CLI_CONFIG_DIR: str = "signal-cli_config"
    SOCKET_FILE: str = "/tmp/signal-cli/socket"
    STORAGE_PROVIDER_NUMBER_MAP_DB: str = "file"
    STORAGE_PROVIDER_PROCESS_DB: str = "file"
    STORAGE_PROVIDER_STATE_DB: str = "file"
    STORAGE_PROVIDER_USER_DB: str = "file"
    VERSION: str = "0.0.1"
    VOLUME_PATH: str = "/tmp/signal-bot"


def get_storage_mapping():
    storage_mapping = {
        "file": JsonStorage,
        "fs": FsStorage,
        "memory": MemoryStorage,
    }
    return storage_mapping


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
            "redirect_uris": [
                "http://127.0.0.1:8000/api/v1/auth/callback",
                "http://signal-bot.nazes.fr/api/v1/auth/callback",
            ],
        }
    }


@lru_cache()
def is_allow_to_execute_self_send():
    settings = get_settings()
    return settings.ALLOW_EXECUTE_SELF_SEND == "y"


@lru_cache()
def get_signal_cli_config_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.SIGNAL_CLI_CONFIG_DIR


@lru_cache
def get_attachments_path():
    settings = get_settings()
    return settings.VOLUME_PATH + "/" + settings.SIGNAL_CLI_CONFIG_DIR + "/attachments"


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


def get_formater(properties, debug) -> MessageFormater:
    return JsonRpcFormater(
        account=properties.account,
        receiver_type=properties.receiver_type,
        receiver=properties.receiver,
        debug=debug,
    )


def get_chatter(queue, properties, phonebook) -> Chatter:
    settings = get_settings()
    mapping = {
        "signal": SignalChatter,
        "facebook": FacebookChatter,
    }
    formater = get_formater(properties, settings.ALLOW_EXECUTE_SELF_SEND == "y")
    return mapping[settings.CHATTER_CLIENT](
        queue=queue,
        formater=formater,
        socket_file=settings.SOCKET_FILE,
        phonebook=phonebook,
    )


def get_queue_storage() -> QueueStorage:
    settings = get_settings()
    mapping = {
        "deque": DequeStorage,
    }
    return mapping[settings.QUEUE_STORAGE_PROVIDER](settings.QUEUE_STORAGE_MAXLEN)


def get_user_db() -> ObjectStorage:
    settings = get_settings()
    mapping = {"file": JsonStorage}
    return mapping[settings.STORAGE_PROVIDER_NUMBER_MAP_DB](get_db_number_map_path())


def get_attachment_format_from_files(files_path: List[str]) -> List[str]:
    attachments = list()
    for file_path in files_path:
        with open(file_path, "r") as attachment:
            encoded_string = b64encode(attachment.read())
            data_type = mimetypes.guess_type(file_path)
            attachments.append(f"data:{data_type};base64,{encoded_string}")
    return attachments
