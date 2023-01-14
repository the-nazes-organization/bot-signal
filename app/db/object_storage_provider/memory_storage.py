from app.db.object_storage import ObjectStorage


class MemoryStorage(ObjectStorage):
    """
    MemoryStorage is a class that implements the ObjectStorage interface
    and is used to store data in memory.
    In memory, the data is stored in a dictionary.
    """

    def __init__(self) -> None:
        self.data = {}

    def get(self, key: str) -> any:
        return self.data.get(key)

    def put(self, key: str, value: any) -> None:
        self.data[key] = value

    def delete(self, key: str) -> None:
        if key in self.data:
            del self.data[key]

    def get_all(self) -> any:
        return self.data

    def put_all(self, data: any) -> None:
        self.data = data

    def clear(self) -> None:
        self.data = {}
