from pydantic import BaseSettings
from functools import lru_cache


class GoogleSettings(BaseSettings):
    CLIENT_SECRET_FILE: str = "signal_bot/backend/secrets/client_secret.google.test.json"
    SCOPES: list[str] = ["https://www.googleapis.com/auth/userinfo.email", "openid"]
    #needs cleansing
    CALLBACK_URL: str = "http://127.0.0.1:8000/api/v1/auth/callback"
    AUTH_ANTIFORGERY_FILE: str = "signal_bot/backend/secrets/auth_antiforgery_tokens.json"
    CLIENT_ID: str = "client_id"
    CLIENT_SECRET: str = "client_secret"

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    MY_TEST_ENV: str = "hello"
    GOOGLE: GoogleSettings = GoogleSettings()
    WHITELIST_FILE: str = "signal_bot/backend/secrets/whitelist.json"


@lru_cache()
def get_settings():
	return Settings()