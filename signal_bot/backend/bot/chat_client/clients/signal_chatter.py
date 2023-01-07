from datetime import datetime
import logging
import socket
from typing import List
from uuid import uuid4


from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.formater import MessageFormater

from signal_bot.backend.core.config import get_number_map_db

from signal_bot.backend.db.queue_storage import QueueStorage

from signal_bot.backend.schemas.data_formated import (
    DataFormated,
    User,
    Message
)

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

    def read_message(self) -> DataFormated:
        raw_message = self._get_last_message()
        self.logger.debug("Received message: %s", raw_message)
        data = self.formater.deformat(raw_message)
        return data

    def send_message(
        self, message: str | None=None,
        attachments: List[str] | None=None,
        quote_id : str | None=None
    ):
        """Send message to signal

        Args:
            message (str | None, optional): Defaults to None.
            text of the message, see @mentions.


            attachments (List, optional): Defaults to None.
            list of attachments to send with message,
            the strings must be in the format of RPC 2397 with data in b64 encoding.

            quote_id (str | None, optional): Defaults to None.
            id of the message you want to quote,
            previous messages are found in the queue or directly in the data
            param of the commands.
                
        
        @mentions : to mention someone just use this syntax in the message param:
        "Hello @@fela"
        Syntax : @@{name of the person to mention} in the message str
        """

        if message is None and attachments is None and quote_id is None:
            raise NotImplementedError("Send message without params")

        quote_params = self._get_quote_params_from_history(quote_id)

        # save message in queue
        if message is not None:
            self._save_message_in_queue(message)

        data = self.formater.format_message(message, attachments, **quote_params)

        self._send_data(data)
    
    def send_reaction(self, emoji: str, target_author: str, target_sent_at: datetime):
        data = self.formater.format_reaction(emoji, target_author, target_sent_at)
        self._send_data(data)

    def send_typing(self):
        data = self.formater.format_typing()
        self._send_data(data)

    def get_history(self, nb_messages: int = 10) -> List[DataFormated]:
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

    def _get_quote_params_from_history(self, quote_id: str | None) -> dict:
        if quote_id is not None:
            for data in self.queue.get_all():
                if data.id == quote_id:
                    return {
                        "quote_author": data.user.phone,
                        "quote_sent_at": data.sent_at
                    }
            raise LookupError("Can't found specified quote_id in history")
        return {}
    
    def _save_message_in_queue(
        self,
        message: str
    ):
        self.queue.put(
            DataFormated(
                id=str(uuid4()),
                user=User(
                    nickname="LordBot",
                    phone=self._get_bot_phone_from_number_map(get_number_map_db().get_all()),
                    db_name="bot"
                ),
                message=Message(
                    text=message
                ),
                sent_at=datetime.today()
            )
        )
    
    def _get_bot_phone_from_number_map(self, data: dict):
        for phone, name in data.items():
            if name == "bot":
                return phone
        raise LookupError("Can't find bot number in number_map")
