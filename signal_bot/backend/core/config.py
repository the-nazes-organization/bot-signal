from functools import lru_cache

from pydantic import BaseSettings


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = "google_client_id"
    CLIENT_SECRET: str = "google_client_secret"
    SCOPES: list[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]
    AUTH_ANTIFORGERY_FILE: str = "signal_bot/local_db/auth_antiforgery_tokens.json"

    class Config:
        env_prefix = "GOOGLE_"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    WHITELIST_FILE: str = "signal_bot/local_db/whitelist.json"
    GOOGLE: GoogleSettings = GoogleSettings()
    PYTHON_BOT_FILE: str = "signal_bot/backend/message_client/bot_startup.py"
    SOCKET_FILE: str = "/tmp/signal_cli/socket"
    STORAGE_PROVIDER_USER_DB: str = "file"
    STORAGE_PROVIDER_STATE_DB: str = "file"
    STORAGE_PROVIDER_PROCESS_DB: str = "file"
    DB_USER: str = "signal_bot/local_db/users.json"
    DB_STATE: str = "signal_bot/local_db/state.json"
    DB_PROCESS: str = "signal_bot/local_db/processes.json"


@lru_cache()
def get_settings():
    return Settings()
