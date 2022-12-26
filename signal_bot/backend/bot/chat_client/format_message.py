import json
import uuid

from abc import ABC, abstractmethod

class MessageFormater(ABC):

    @abstractmethod
    def format_message(self, message):
        pass

    @abstractmethod
    def format_reaction(self, emoji, target_author, target_timestamp):
        pass

    @abstractmethod
    def deformat(self, data):
        pass


class JsonRpcFormater(MessageFormater):

    def __init__(self, account, receiver_type, receiver):
        self.account = account
        self.receiver_type = receiver_type
        self.receiver = receiver

    def _get_base_rpc_obj(self, method: str):
        rpc_obj = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {"account": self.account},
            "id": str(uuid.uuid4()),
        }
        if self.receiver_type == "group_id":
            rpc_obj["params"]["groupId"] = self.receiver
        elif self.receiver_type == "recipient":
            rpc_obj["params"]["recipient"] = [self.receiver]
        return rpc_obj

    def format_message(self, message):
        rpc_obj = self._get_base_rpc_obj("send")
        rpc_obj["params"]["message"] = message
        return json.dumps(rpc_obj)

    def format_reaction(
        self, emoji: str, target_author: str, target_timestamp: int
    ):
        rpc_obj = self._get_base_rpc_obj("sendReaction")
        rpc_obj["params"]["emoji"] = emoji
        rpc_obj["params"]["targetAuthor"] = target_author
        rpc_obj["params"]["targetTimestamp"] = target_timestamp
        return json.dumps(rpc_obj)

    def deformat(self, data: str) -> dict:
        # Maybe check if rpc is in correct form and raise warning if not
        data_obj: dict = json.loads(data)

        if (
            data_obj.get("method") is not None
            and data_obj.get("params") is not None
            and data_obj["params"].get("envelope")
        ):
            return {"type": "message", "params": data_obj["params"]["envelope"]}
        return {"type": "useless"}
