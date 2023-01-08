from datetime import datetime

from app.bot.chat_client.chatter import Chatter
from app.bot.chat_client.clients.signal.formater import MessageFormater


class FacebookChatter(Chatter):
    def __init__(self, formater: MessageFormater) -> None:
        self.formater = formater

    def read_message(self):
        raise NotImplementedError

    def send_message(self, message: str, **kwargs):
        raise NotImplementedError

    def send_reaction(self, emoji: str, target_author: str, target_sent_at: datetime):
        raise NotImplementedError
