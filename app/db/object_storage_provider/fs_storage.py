import os
from pathlib import Path

from app.db.object_storage import ObjectStorage


class FsStorage(ObjectStorage):
    """
    FsStorage is a class that implements the ObjectStorage interface
    and is used to store data in the file system.
    In the file system, the data is stored in plain text.
    """

    def __init__(self, path) -> None:
        self.storage_path = path
        self.init()

    def init(self) -> None:
        if not Path(self.storage_path).is_dir():
            Path().mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> any:
        data_path = self._get_data_path(key)
        try:
            self._file_exists(data_path)
        except FileNotFoundError:
            return None
        with open(data_path, "r") as open_file:
            data = open_file.read()
        return data

    def put(self, key: str, value: any) -> None:
        data_path = self._get_data_path(key)

        if not Path(data_path).parent.is_dir():
            Path(data_path).parent.mkdir(parents=True, exist_ok=True)

        with open(data_path, "w") as open_file:
            open_file.write(value)

    def delete(self, key: str) -> None:
        data_path = self._get_data_path(key)
        os.remove(data_path)
        while not os.listdir(Path(data_path).parent):
            os.rmdir(Path(data_path).parent)
            data_path = Path(data_path).parent
            if data_path == self.storage_path:
                break

    def get_all(self) -> any:
        data = {}
        for file in Path(self.storage_path).rglob("*"):
            if file.is_file():
                file_key = str(file.relative_to(self.storage_path))
                data[file_key] = self.get(file)
        return data

    def put_all(self, data: any) -> None:
        for key, value in data.items():
            self.put(key, value)

    def _get_data_path(self, key: str) -> str:
        return str(Path(self.storage_path, key))

    def _file_exists(self, path: str) -> None:
        if not Path(path).is_file():
            print("File not found: " + path)
            raise FileNotFoundError("File not found: " + path)
