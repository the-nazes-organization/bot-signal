from fastapi import Query

from signal_bot.backend.core.config import (
    get_settings,
    get_db_user_path,
    get_db_state_path,
    get_db_process_path,
)
from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.db.object_storage_provider.file_storage import FileStorage

storage_mapping = {"file": FileStorage}


async def check_account_number(
    account: str = Query(description="Number of the phone for the account", regex="^[0-9]*$")
):
    return "+" + account


async def get_user_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_USER_DB](get_db_user_path())


async def get_state_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_STATE_DB](get_db_state_path())


async def get_process_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_PROCESS_DB](get_db_process_path())
