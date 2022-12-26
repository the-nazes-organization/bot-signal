
import socket

from signal_bot.backend.bot.chat_client.format_message import MessageFormater
from signal_bot.backend.bot.chat_client.chatter import Chatter


CHATTER_BUFFSIZE = 4096


class SignalChatter(Chatter):
    def __init__(self,socket_file:str, formater: MessageFormater) -> None:
        self.formater = formater
        self.cached_message = b""
        self.chat_location = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.chat_location.connect(socket_file)

    def read_message(self):
        raw_message = self._get_last_message()
        message = self.formater.deformat(raw_message)
        return message

    def send_message(self, message: str):
        data = self.formater.format_message(message)
        self._send_data(data)

    def send_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        data = self.formater.format_reaction(emoji, target_author, target_timestamp)
        self._send_data(data)

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