import json

from signal_bot.backend.db.object_storage import ObjectStorage


class FileStorage(ObjectStorage):
    """
    FileStorage is a class that implements the ObjectStorage interface
    and is used to store data in a file.
    """

    def __init__(self, path) -> None:
        self.file = path

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
        with open(self.file, "r") as fd:
            data = json.load(fd)
        return data

    def _put_data_to_file(self, data: any) -> None:
        with open(self.file, "w") as fd:
            json.dump(data, fd)
