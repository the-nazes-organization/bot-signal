import json

from signal_bot.backend.db.object_storage import ObjectStorage


class FileStorage(ObjectStorage):
    """
    FileStorage is a class that implements the ObjectStorage interface
    and is used to store data in a file.
    """

    def __init__(self, path) -> None:
        self.file_path = path

    def get(self, key: str) -> any:
        data = self._get_data_from_file()
        return data.get(key)

    def put(self, key: str, value: any) -> None:
        data = self._get_data_from_file()
        data[key] = value
        self._put_data_to_file(data)

    def delete(self, key: str) -> None:
        data = self._get_data_from_file()
        if key in data:
            del data[key]
            self._put_data_to_file(data)

    def get_all(self) -> any:
        return self._get_data_from_file()

    def put_all(self, data: any) -> None:
        self._put_data_to_file(data)

    def _get_data_from_file(self) -> any:
        with open(self.file_path, "r", encoding="utf-8") as open_file:
            data = json.load(open_file)
        return data

    def _put_data_to_file(self, data: any) -> None:
        with open(self.file_path, "w", encoding="utf-8") as open_file:
            json.dump(data, open_file, indent=4)
