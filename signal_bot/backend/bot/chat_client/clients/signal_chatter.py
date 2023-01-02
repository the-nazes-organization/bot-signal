import json
import logging
import socket

from signal_bot.backend.bot.chat_client.format_message import MessageFormater
from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.bot.chat_client.chatter import Chatter


CHATTER_BUFFSIZE = 4096


class SignalChatter(Chatter):
    def __init__(
        self, socket_file: str, formater: MessageFormater, queue: QueueStorage
    ) -> None:
        self.queue = queue
        self.formater = formater
        self.cached_message = b""
        self.chat_location = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.chat_location.connect(socket_file)
        self.logger = logging.getLogger(__name__)

    def read_message(self):
        raw_message = self._get_last_message()
        self.logger.debug("Received message: %s", raw_message)
        message = self.formater.deformat(raw_message)
        return message

    def send_message(self, message: str, **kwargs):
        data = self.formater.format_message(message, **kwargs)
        #save message in queue
        self.queue.put(json.loads(data))
        self._send_data(data)

    def send_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        data = self.formater.format_reaction(emoji, target_author, target_timestamp)
        self._send_data(data)

    def send_typing(self):
        data = self.formater.format_typing()
        self._send_data(data)

    def get_history(self, nb_messages: int = 10) -> list:
        return self.queue.get_n_last(nb_messages)

    def _get_last_message(self, message_end_marker=b"\n") -> str:
        data = self.cached_message

        while (index_marker := data.find(message_end_marker)) == -1:
            data += self._receive_data()

        last_message = data[:index_marker]
        self.cached_message = data[index_marker + 1 :]
        return last_message

    def _receive_data(self) -> bytes:
        data = self.chat_location.recv(CHATTER_BUFFSIZE)
        return data

    def _send_data(self, data: str):
        self.chat_location.sendall(bytes(data.encode()) + b"\n")
        self.logger.debug(f"Just sent this data : {data}")
