from fastapi import Query

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.db import ObjectStorage
from signal_bot.backend.db.provider.FileStorage import FileStorage

async def check_account_number(account: str = Query(description="Number of the phone for the account", regex="^[0-9]*$")):
    return "+" + account


storage_mapping = {
    "file": FileStorage
}

async def get_user_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_USER_DB](settings.DB_USER)

async def get_state_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_STATE_DB](settings.DB_STATE)


async def get_process_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_PROCESS_DB](settings.DB_PROCESS)

