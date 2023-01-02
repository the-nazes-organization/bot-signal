import json
import uuid

from abc import ABC, abstractmethod

class MessageFormater(ABC):

    @abstractmethod
    def format_message(self, message, **kwargs):
        pass

    @abstractmethod
    def format_reaction(self, emoji, target_author, target_timestamp):
        pass

    @abstractmethod
    def format_typing(self):
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

    def format_message(self, message, **kwargs):
        """Format message with possible additional data

        Args:
            message (str): message to send

            attachments (list): list of str in the format RFC 2397 for attachments
            quote_author (str): who's the author to quote from
            quote_timestamp (str): timestamp of the message to quote from
            mention (dict) = {
                target (str): phone number of the person mentioned
                start (int): where in the string gof the message the mention starts at
                length (int): from start var index in string to where does the mention stops
            }

        Returns:
            dict: formated data
        """
        rpc_obj = self._get_base_rpc_obj("send")
        rpc_obj["params"]["message"] = message

        if (attachments := kwargs.get("attachments")) is not None:
            rpc_obj["params"]["attachments"] = attachments

        if (quote_author := kwargs.get("quote_author")) is not None\
        and (quote_timestamp := kwargs.get("quote_timestamp")) is not None:
            rpc_obj["params"]["quoteAuthor"] = quote_author
            rpc_obj["params"]["quoteTimestamp"] = quote_timestamp

        if (mention_obj := kwargs.get("mention")) is not None:
            rpc_obj["params"]["mention"] = self._get_mention_string(**mention_obj)

        return json.dumps(rpc_obj)
    
    def format_reaction(
        self, emoji: str, target_author: str, target_timestamp: int
    ):
        rpc_obj = self._get_base_rpc_obj("sendReaction")
        rpc_obj["params"]["emoji"] = emoji
        rpc_obj["params"]["targetAuthor"] = target_author
        rpc_obj["params"]["targetTimestamp"] = target_timestamp
        return json.dumps(rpc_obj)
    
    def format_typing(self):
        rpc_obj = self._get_base_rpc_obj("sendTyping")
        return json.dumps(rpc_obj)

    def deformat(self, data: str) -> dict:
        method_type = "unknown"
        params = {}

        try:
            data_obj: dict = json.loads(data)
        except ValueError as exc:
            error = exc

        if (
            data_obj.get("method") is not None
            and data_obj.get("params") is not None
            and data_obj["params"].get("envelope") is not None
        ):
            params = data_obj["params"]["envelope"]
            if data_obj.get("method") == "receive" and data_obj["params"]["envelope"].get("dataMessage"):
                method_type = "message"
            elif data_obj.get("method") == "receive" and data_obj["params"]["envelope"].get("typingMessage"):
                method_type = "typing"

        return {"type": method_type, "params": params}

    def _get_mention_string(self, target: str, start: int, length: int):
        return f"{start}:{length}:{target}"