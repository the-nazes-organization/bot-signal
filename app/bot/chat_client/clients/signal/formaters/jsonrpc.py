import json
import logging
import re
from datetime import datetime
from typing import List
from uuid import uuid4

from app.bot.chat_client.clients.signal.formater import MessageFormater
from app.bot.schema.data_formated import (
    AttachmentData,
    DataFormated,
    Mention,
    Message,
    QuotedMessage,
    Reaction,
    Typing,
    User,
)


class JsonRpcFormater(MessageFormater):
    def __init__(self, account, receiver_type, receiver, debug=False):
        """
        Initialize a JsonRpcFormater object with the given account, receiver_type, and
        receiver.

        Parameters:
        - account (str): The account to send messages from.
        - receiver_type (str): The type of the receiver,
        either "group_id" or "recipient".
        - receiver (str): The ID of the group or recipient to send messages to.
        """
        self.account = account
        self.receiver_type = receiver_type
        self.receiver = receiver
        self.logger = logging.getLogger(__name__)
        self.debug = debug

    def _get_base_rpc_obj(self, method: str):
        """
        Return a base JSON-RPC object with the given method and the account
        and receiver parameters set.

        Parameters:
        - method (str): The method of the JSON-RPC object.

        Returns:
        - dict: The base JSON-RPC object.
        """
        rpc_obj = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {"account": self.account},
            "id": str(uuid4()),
        }
        if self.receiver_type == "group_id":
            rpc_obj["params"]["groupId"] = self.receiver
        elif self.receiver_type == "recipient":
            rpc_obj["params"]["recipient"] = [self.receiver]
        return rpc_obj

    def format_message(
        self,
        all_names=None,
        message: str = None,
        attachments: List[str] = None,
        quote_author: str = None,
        quote_sent_at: datetime = None,
    ):
        rpc_obj = self._get_base_rpc_obj("send")

        if attachments:
            rpc_obj["params"]["attachments"] = attachments

        if quote_author and quote_sent_at:
            rpc_obj["params"]["quoteAuthor"] = quote_author
            rpc_obj["params"]["quoteTimestamp"] = self._get_timestamp_from_datetime(
                quote_sent_at
            )

        if message and (
            mentions := self._create_mentions_from_message(message, all_names)
        ):
            rpc_obj["params"]["mentions"] = mentions

        rpc_obj["params"]["message"] = message
        return json.dumps(rpc_obj)

    def _create_mentions_from_message(
        self, message: str, all_names
    ) -> List[str] or None:
        mentions = list()

        for match in re.finditer(r"@{2}(\w+)", message):
            mention_target = None
            matched_name = match.group(1)
            for number, name in all_names.items():
                if name == matched_name:
                    mention_target = number
                    break
            if mention_target is None:
                continue

            start = match.start()
            length = match.end() - match.start()
            mentions.append(f"{start}:{length}:{mention_target}")
        return mentions if len(mentions) > 0 else None

    def format_reaction(self, emoji: str, target_author: str, target_sent_at: datetime):
        """
        Format a reaction with the given parameters into a JSON-RPC object.

        Parameters:
        - emoji (str): The emoji of the reaction.
        - target_author (str): The author of the message to react to.
        - target_sent_at (datetime): The time the message to react to was sent.

        Returns:
        - str: The JSON-RPC object representing the reaction.
        """
        rpc_obj = self._get_base_rpc_obj("sendReaction")
        rpc_obj["params"]["emoji"] = emoji
        rpc_obj["params"]["targetAuthor"] = target_author
        rpc_obj["params"]["targetTimestamp"] = self._get_timestamp_from_datetime(
            target_sent_at
        )
        return json.dumps(rpc_obj)

    def format_typing(self):
        """
        Format a typing notification into a JSON-RPC object.

        Returns:
        - str: The JSON-RPC object representing the typing notification.
        """
        rpc_obj = self._get_base_rpc_obj("sendTyping")
        return json.dumps(rpc_obj)

    def deformat(self, data: str) -> DataFormated or None:
        """
        Deformat the given JSON-RPC object into a DataFormated object.

        Parameters:
        - data (str): The JSON-RPC object to deformat.

        Returns:
        - DataFormated or None: The deformatted data, or None if the JSON-RPC object
        could not be decoded.
        Raises:
        - ValueError: If the JSON-RPC object could not be decoded.
        """
        try:
            raw = self._get_raw_data_from_json(data)
        except json.JSONDecodeError:
            self.logger.warning("Json decode failed", exc_info=1)
            raise ValueError("Json decode error")
        return self._deformat_into_data_formated(raw)

    def _get_raw_data_from_json(self, data: str) -> dict:
        """
        Decode the given JSON-RPC object into a dictionary.

        Parameters:
        - data (str): The JSON-RPC object to decode.

        Returns:
        - dict: The decoded JSON-RPC object.

        Raises:
        - json.JSONDecodeError: If the JSON-RPC object could not be decoded.
        """
        return json.loads(data)

    def _deformat_into_data_formated(self, data: dict) -> DataFormated | None:
        envelope = self._get_envelope_and_check_validity(data)
        if not envelope:
            return None

        formated = self._get_basic_formated_data(envelope)

        # Used for testing in local with your own phone
        data_message = self._get_data_message_from_envelope(envelope)

        formated.message = self._get_message_formated_data(data_message)
        formated.typing = self._get_typing_formated_data(envelope.get("typingMessage"))
        formated.reaction = self._get_reaction_formated_data(data_message)
        formated.attachments = self._get_attachments_formated_data(data_message)

        return formated

    def _get_envelope_and_check_validity(self, data: dict) -> dict | None:
        envelope = None
        if (
            data.get("method") == "receive"
            and data.get("params")
            and data["params"].get("envelope")
        ):
            envelope = data["params"]["envelope"]
            group_id = self._get_group_id_from_envelope(envelope)

            # Check if data is according to formater receiver presets
            if (
                self.receiver_type == "recipient"
                and (
                    group_id is not None
                    or envelope.get("sourceNumber") != self.receiver
                )
            ) or (self.receiver_type == "group_id" and group_id != self.receiver):
                envelope = None

        return envelope

    def _get_group_id_from_envelope(self, envelope: dict) -> str | None:
        group_spot = {}
        data_message = self._get_data_message_from_envelope(envelope)
        if envelope.get("typingMessage"):
            group_spot = envelope["typingMessage"]
        elif data_message and data_message.get("groupInfo"):
            group_spot = data_message["groupInfo"]
        return group_spot.get("groupId")

    def _get_data_message_from_envelope(self, envelope: dict) -> dict | None:
        if (
            envelope.get("syncMessage")
            and envelope["syncMessage"].get("sentMessage")
            and self.debug is True
        ):
            return envelope["syncMessage"]["sentMessage"]
        return envelope.get("dataMessage")

    def _get_basic_formated_data(self, data: dict) -> DataFormated:
        return DataFormated(
            id=str(uuid4()),
            user=User(nickname=data.get("sourceName"), phone=data.get("sourceNumber")),
            sent_at=self._get_datetime_from_timestamp(data.get("timestamp")),
        )

    def _get_message_formated_data(self, data: dict) -> Message | None:
        if data and data.get("message"):
            return Message(
                text=data.get("message"),
                quote=self._get_quote_formated_data(data.get("quote")),
                mentions=self._get_mentions_formated_data(data.get("mentions")),
            )
        return None

    def _get_quote_formated_data(self, data: dict) -> QuotedMessage | None:
        if data:
            return QuotedMessage(
                text=data.get("text"),
                author=User(
                    nickname=data.get("author"), phone=data.get("authorNumber")
                ),
                mentions=self._get_mentions_formated_data(data.get("mentions")),
            )
        return None

    def _get_mentions_formated_data(self, data: dict) -> List[Mention] | None:
        mentions = None
        if data and len(data) > 0:
            mentions = list()
            for item in data:
                mentions.append(
                    Mention(
                        user=User(nickname=item.get("name"), phone=item.get("number")),
                        start=item.get("start"),
                        length=item.get("length"),
                    )
                )
        return mentions

    def _get_typing_formated_data(self, data: dict) -> Typing | None:
        if data:
            return Typing(status=data.get("action"))
        return None

    def _get_reaction_formated_data(self, data: dict) -> Reaction | None:
        if data and data.get("reaction"):
            data = data.get("reaction")
            return Reaction(
                reaction=data.get("emoji"),
                target_author=User(
                    nickname=data.get("targetAuthor"),
                    phone=data.get("targetAuthorNumber"),
                ),
                sent_at=self._get_datetime_from_timestamp(
                    data.get("targetSentTimestamp")
                ),
            )
        return None

    def _get_attachments_formated_data(self, data: dict) -> List[AttachmentData] | None:

        attachments = None
        if data and data.get("attachments") and len(data.get("attachments")) > 0:
            attachments = list()
            for item in data.get("attachments"):
                attachments.append(
                    AttachmentData(
                        content_type=item.get("contentType"),
                        filename=item.get("filename"),
                        size=item.get("size"),
                    )
                )
        return attachments

    def _get_datetime_from_timestamp(self, timestamp: float) -> datetime:
        # Receiving timestamp in millisec transform to sec
        return datetime.fromtimestamp(timestamp / 1000.0)

    def _get_timestamp_from_datetime(self, time: datetime) -> float:
        # Transform timestamp back to millisec
        return time.timestamp() * 1000
