from abc import ABC, abstractmethod


class ObjectStorage(ABC):
    """
    ObjectStorage is an interface that defines the methods that
    must be implemented by the classes that will be used to store
    data.
    """

    @abstractmethod
    def get(self, key: str) -> any:
        pass

    @abstractmethod
    def put(self, key: str, value: any) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> any:
        pass

    @abstractmethod
    def put_all(self, data: any) -> None:     
        pass