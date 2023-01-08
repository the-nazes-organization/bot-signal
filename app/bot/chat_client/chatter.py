from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class Chatter(ABC):
    @abstractmethod
    def read_message(self):
        pass

    @abstractmethod
    def send_message(self,
        message: str | None=None,
        attachments: List[str] | None=None,
        quote_id : str | None=None
    ):
        pass

    @abstractmethod
    def send_reaction(self, emoji: str, target_author: str, target_sent_at: datetime):
        pass

    @abstractmethod
    def send_typing(self):
        pass

    @abstractmethod
    def get_history(self, nb_messages: int=10):
        pass


class ChatterHolder:
    _instance = None

    def __init__(self, chatter: Chatter) -> None:
        if self._instance is None:
            self.__class__._instance = chatter

    @classmethod
    def get_chatter(cls) -> Chatter:
        return cls._instance