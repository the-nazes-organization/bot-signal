from pydantic import BaseSettings
from functools import lru_cache


class GoogleSettings(BaseSettings):
    CLIENT_ID: str = "google_client_id"
    CLIENT_SECRET: str = "google_client_secret"
    SCOPES: list[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]
    AUTH_ANTIFORGERY_FILE: str = "signal_bot/local_db/auth_antiforgery_tokens.json"

    class Config():
        env_prefix = "GOOGLE_"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    WHITELIST_FILE: str = "signal_bot/local_db/whitelist.json"
    GOOGLE: GoogleSettings = GoogleSettings()


@lru_cache()
def get_settings():
	return Settings()