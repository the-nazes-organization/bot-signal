from collections import deque

from app.db.queue_storage import QueueStorage


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

    def get_n_last(self, nb_elem: int = 1) -> any:
        res = []
        for i in range(nb_elem):
            elem = self.get(i)
            if elem is None:
                break
            res.append(elem)
        return res

    def put(self, value: any) -> None:
        self.queue.appendleft(value)

    def get_all(self) -> any:
        return list(self.queue)

    def put_all(self, datas: any) -> None:
        for value in datas:
            self.put(value)
