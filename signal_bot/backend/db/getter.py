from signal_bot.backend.db.object_storage import ObjectStorage
from signal_bot.backend.db.object_storage_provider.file_storage import FileStorage
from signal_bot.backend.core.config import get_settings, get_db_number_map_path

storage_mapping = {
    "file": FileStorage
}

def get_number_map_db() -> ObjectStorage:
    settings = get_settings()
    return storage_mapping[settings.STORAGE_PROVIDER_PROCESS_DB](
        get_db_number_map_path()
    )

def get_name_by_number(number: str):
    db_obj = get_number_map_db()
    return db_obj.get(number)

def get_all_numbers() -> list:
    db_obj = get_number_map_db()
    return list(db_obj.get_all().values())
