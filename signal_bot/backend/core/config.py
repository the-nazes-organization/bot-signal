from pydantic import BaseSettings
from functools import lru_cache



class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Signal Bot"
    MY_TEST_ENV: str = "hello"

@lru_cache()
def get_settings():
	return Settings()