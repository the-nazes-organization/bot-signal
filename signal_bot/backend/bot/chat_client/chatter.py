from abc import ABC, abstractmethod


class Chatter(ABC):
    @abstractmethod
    def read_message(self):
        pass

    @abstractmethod
    def send_message(self, message: str, **kwargs):
        pass

    @abstractmethod
    def send_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        pass
