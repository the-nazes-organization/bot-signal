from fastapi import Path, Query

from signal_bot.backend.core.config import (
    get_db_number_map_path,
    get_db_process_path,
    get_db_state_path,
    get_db_user_path,
    get_settings,
)
from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.db.object_storage_provider.file_storage import FileStorage

storage_mapping = {"file": FileStorage}

settings = get_settings()


async def check_account_number(
    account: str = Query(
        description="Number of the phone for the account (needs to be url encoded)",
        regex=settings.NUMBER_FORMAT_REGEX,
    )
):
    return account


async def check_path_number(
    number: str = Path(
        description="Phone number of the associated name (needs to be url encoded)",
        regex=settings.NUMBER_FORMAT_REGEX,
    )
):
    return number


async def get_user_db() -> ObjectStorage:
    return storage_mapping[settings.STORAGE_PROVIDER_USER_DB](get_db_user_path())


async def get_state_db() -> ObjectStorage:
    return storage_mapping[settings.STORAGE_PROVIDER_STATE_DB](get_db_state_path())


async def get_process_db() -> ObjectStorage:
    return storage_mapping[settings.STORAGE_PROVIDER_PROCESS_DB](get_db_process_path())


async def get_number_map_db() -> ObjectStorage:
    return storage_mapping[settings.STORAGE_PROVIDER_NUMBER_MAP_DB](
        get_db_number_map_path()
    )
