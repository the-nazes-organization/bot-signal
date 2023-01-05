import json
import logging
import socket
from typing import List

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.format_message import MessageFormater
from signal_bot.backend.db.queue_storage import QueueStorage

from signal_bot.backend import schemas

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

    def read_message(self) -> schemas.DataFormated:
        raw_message = self._get_last_message()
        self.logger.debug("Received message: %s", raw_message)
        data = self.formater.deformat(raw_message)
        return data

    def send_message(
        self, message: str | None=None,
        attachments: List(str) | None=None,
        quote_id : str | None=None
    ):
        """Send message to signal

        Args:
            message (str | None, optional): text of the message
            see mentions. Defaults to None.

            attachments (List, optional): list of attachments to send with message,
            the strings must be in the format of RPC 2397. Defaults to None.

            quote_id (str | None, optional): id of the message you want to quote,
            previous messages are found in the queue or directly in the data
            param of the commands. Defaults to None.
        
        @mentions : to mention someone just use this syntax in the message param:
        "Hello @@fela"
        Syntax : @@{name of the person to mention} in the message str
        """

        quote_data = self._get_quote_data_from_history(quote_id)
        data = self.formater.format_message(message, attachments, **quote_data)
        # save message in queue
        self.queue.put(json.loads(data))
        self._send_data(data)
    
    def send_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        data = self.formater.format_reaction(emoji, target_author, target_timestamp)
        self._send_data(data)

    def send_typing(self):
        data = self.formater.format_typing()
        self._send_data(data)

    def get_history(self, nb_messages: int = 10) -> List[schemas.DataFormated]:
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
        self.logger.debug("Just sent this data : %s", data)

    def _get_quote_data_from_history(self, quote_id: str | None) -> dict:
        if quote_id is not None:
            for data in self.queue.get_all():
                if data.id == quote_id:
                    return {
                        "quote_author": data.user.phone,
                        "quote_sent_at": data.sent_at
                    }
            raise LookupError("Can't found specified quote_id in history")
        return {}