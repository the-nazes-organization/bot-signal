from abc import ABC, abstractmethod
from typing import List

from signal_bot.backend import schemas

class Chatter(ABC):
    @abstractmethod
    def read_message(self) -> schemas.DataFormated | None :
        pass

    @abstractmethod
    def send_message(self,
        message: str | None=None,
        attachments: List(str) | None=None,
        quote_id : str | None=None
    ):
        pass

    @abstractmethod
    def send_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        pass

    @abstractmethod
    def send_typing(self):
        pass

    @abstractmethod
    def get_history(self, nb_messages: int=10) -> List[schemas.DataFormated]:
        pass
