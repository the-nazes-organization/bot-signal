import socket
import json
import uuid

from signal_bot.backend.core.singleton import Singleton

CHATTER_BUFFSIZE = 4096

class SocketChatter(metaclass=Singleton):

    def __init__(self, socket_file: str, account: str, receiver_type: str, receiver: str) -> None:
        self.account = account
        self.receiver_type = receiver_type
        self.receiver = receiver
        self.cached_message = b""

        self.chat_location = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.chat_location.connect(socket_file)

    def read_message(self):
        raw_message = self._get_last_message()
        message = self._deformat_rpc(raw_message)
        return message

    def send_message(self, message: str):
        data = self._format_message_rpc(message)
        self._send_data(data)
    
    def send_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        data = self._format_reaction_rpc(emoji, target_author, target_timestamp)
        self._send_data(data)

    def _format_message_rpc(self, message: str) -> str:
        rpc_obj = self._get_base_rpc_obj("send")
        rpc_obj["params"]["message"] = message
        return json.dumps(rpc_obj)
    
    def _format_reaction_rpc(self, emoji: str, target_author: str, target_timestamp: int):
        rpc_obj = self._get_base_rpc_obj("sendReaction")
        rpc_obj["params"]["emoji"] = emoji
        rpc_obj["params"]["targetAuthor"] = target_author
        rpc_obj["params"]["targetTimestamp"] = target_timestamp
        return json.dumps(rpc_obj)

    def _get_base_rpc_obj(self, method: str):
        rpc_obj = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {
                "account": self.account
            },
            "id": str(uuid.uuid4())
        }
        if self.receiver_type == "group_id":
            rpc_obj["params"]["groupId"] = self.receiver
        elif self.receiver_type == "recipient":
            rpc_obj["params"]["recipient"] = [self.receiver]
        return rpc_obj

    def _deformat_rpc(self, data: str) -> dict:
        #Maybe check if rpc is in correct form and raise warning if not
        data_obj: dict = json.loads(data)

        if data_obj.get("method") is not None\
        and data_obj.get("params") is not None\
        and data_obj["params"].get("envelope"):
            return {
                "type": "message",
                "params": data_obj["params"]["envelope"]
            }

        return {"type": "useless"}


    def _get_last_message(self, message_end_marker = b"\n") -> str:
        data = self.cached_message

        while (index_marker := data.find(message_end_marker)) == -1:
            data += self._receive_data()

        last_message = data[:index_marker]
        self.cached_message = data[index_marker + 1:]
        return last_message

    def _receive_data(self) -> bytes:
        data = self.chat_location.recv(CHATTER_BUFFSIZE)
        return data
    
    def _send_data(self, data: str):
        self.chat_location.sendall(bytes(data.encode()) + b"\n")