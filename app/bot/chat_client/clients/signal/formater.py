from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class MessageFormater(ABC):
    @abstractmethod
    def format_message(self,
        message: str | None=None,
        attachments: List[str] | None=None,
        quote_author: str | None=None,
        quote_sent_at: datetime | None=None
    ):
        pass

    @abstractmethod
    def format_reaction(self, emoji, target_author, target_sent_at):
        pass

    @abstractmethod
    def format_typing(self):
        pass

    @abstractmethod
    def deformat(self, data):
        pass
