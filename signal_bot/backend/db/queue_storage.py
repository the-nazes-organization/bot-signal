from abc import ABC, abstractmethod


class QueueStorage(ABC):
    """
    QueueStorage is an interface that defines the methods that
    must be implemented by the classes that will be used to store
    data in a queue.
    """

    @abstractmethod
    def get(self) -> any:
        pass

    @abstractmethod
    def get_n_last(self, nb_elem: int = 1) -> any:
        pass

    @abstractmethod
    def put(self, value: any) -> None:
        pass

    @abstractmethod
    def get_all(self) -> any:
        pass

    @abstractmethod
    def put_all(self, datas: any) -> None:
        pass
