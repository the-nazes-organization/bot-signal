from functools import lru_cache

from pydantic import BaseSettings


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = "google_client_id"
    CLIENT_SECRET: str = "google_client_secret"
    SCOPES: list[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]

    class Config: #pylint: disable=too-few-public-methods
        env_prefix = "GOOGLE_"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    GOOGLE: GoogleSettings = GoogleSettings()

    VOLUME_PATH: str = "volume_path"

    SIGNAL_CLI_CONFIG_DIR: str = "signal-cli-config"
    SOCKET_FILE: str = "/tmp/signal-cli/socket"
    PYTHON_BOT_FILE: str = "signal_bot/backend/bot/main.py"

    STORAGE_PROVIDER_USER_DB: str = "file"
    STORAGE_PROVIDER_STATE_DB: str = "file"
    STORAGE_PROVIDER_PROCESS_DB: str = "file"
    STORAGE_PROVIDER_NUMBER_MAP_DB: str = "file"
    DB_USER: str = "db/users.json"
    DB_STATE: str = "db/state.json"
    DB_PROCESS: str = "db/processes.json"
    DB_NUMBER_MAP: str = "db/number_map.json"

    OPENAI_API_KEY: str = "openai_api_key"
    OPENAI_COMPLETION_MAX_TOKEN = "openai_completion_max_token"


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