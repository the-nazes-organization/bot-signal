from collections import deque

from backend.db.queue_storage import QueueStorage


class DequeStorage(QueueStorage):
    """
    FileStorage is a class that implements the ObjectStorage interface
    and is used to store data in a deque collection.
    """

    def __init__(self, maxlen) -> None:
        self.queue = deque(maxlen=maxlen)

    def get(self, index: int = 0) -> any:
        try:
            res = self.queue[index]
        except IndexError:
            res = None
        return res

    def get_n_first(self, nb_elem: int = 1) -> any:
        res = []
        try:
            res = self.queue[:nb_elem]
        except IndexError:
            res = None
        return res

    def put(self, value: any) -> None:
        self.queue.append(value)

    def get_all(self) -> any:
        return self.queue

    def put_all(self, datas: any) -> None:
        for value in datas:
            self.put(value)
