import json
import logging
import re
from datetime import datetime
from uuid import uuid4
from typing import List
from abc import ABC, abstractmethod

from signal_bot.backend import schemas

from signal_bot.backend.core.config import (
    get_number_map_db,
    is_allow_to_execute_self_send
)


class MessageFormater(ABC):
    @abstractmethod
    def format_message(self,
        message: str | None=None,
        attachments: List(str) | None=None,
        quote_author: str | None=None,
        quote_sent_at: datetime | None=None
    ):
        pass

    @abstractmethod
    def format_reaction(self, emoji, target_author, target_timestamp):
        pass

    @abstractmethod
    def format_typing(self):
        pass

    @abstractmethod
    def deformat(self, data) -> schemas.DataFormated | None:
        pass


class JsonRpcFormater(MessageFormater):
    def __init__(self, account, receiver_type, receiver):
        self.account = account
        self.receiver_type = receiver_type
        self.receiver = receiver
        self.logger = logging.getLogger(__name__)

    def _get_base_rpc_obj(self, method: str):
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

    def format_message(self, message: str | None=None,
        attachments: List(str) | None=None,
        quote_author: str | None=None,
        quote_sent_at: datetime | None=None
    ):
        rpc_obj = self._get_base_rpc_obj("send")

        if attachments is not None:
            rpc_obj["params"]["attachments"] = attachments

        if quote_author is not None and quote_sent_at is not None:
            rpc_obj["params"]["quoteAuthor"] = quote_author
            rpc_obj["params"]["quoteTimestamp"] = quote_sent_at

        if (
            message is not None and
            (mention := self._create_mentions_from_message(message)) is not None
        ):
            rpc_obj["params"]["mention"] = mention

        rpc_obj["params"]["message"] = message
        return json.dumps(rpc_obj)

    def _create_mentions_from_message(self, message: str) -> str | None:
        mention = ""
        all_names = get_number_map_db().get_all()

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
            mention += f"{start}:{length}:{mention_target}"
        return mention if mention != "" else None

    def format_reaction(self, emoji: str, target_author: str, target_timestamp: int):
        rpc_obj = self._get_base_rpc_obj("sendReaction")
        rpc_obj["params"]["emoji"] = emoji
        rpc_obj["params"]["targetAuthor"] = target_author
        rpc_obj["params"]["targetTimestamp"] = target_timestamp
        return json.dumps(rpc_obj)

    def format_typing(self):
        rpc_obj = self._get_base_rpc_obj("sendTyping")
        return json.dumps(rpc_obj)


    def deformat(self, data: str) -> schemas.DataFormated | None:
        try:
            raw = self._get_raw_data_from_json(data)
        except json.JSONDecodeError:
            self.logger.warning("Json decode failed", exc_info=1)
            raise ValueError("Json decode error")
        return self._deformat_into_data_formated(raw)


    def _get_raw_data_from_json(self, data: str) -> dict:
        return json.loads(data)

    def _deformat_into_data_formated(self, data: dict) -> schemas.DataFormated | None:
        formated = None
        if (envelope := self._get_envelope_data(data)) is not None:
            formated = self._get_basic_formated_data(
                envelope
            )

            # Used for testing in local with your own phone
            envelope = self._get_sync_message_envelope_if_allowed(envelope)

            formated.message = self._get_message_formated_data(
                envelope.get("dataMessage")
            )

            formated.typing = self._get_typing_formated_data(
                envelope.get("typingMessage")
            )

            formated.reaction = self._get_reaction_formated_data(
                envelope.get("dataMessage")
            )

            formated.attachments = self._get_attachments_formated_data(
                envelope.get("dataMessage")
            )     
        return formated


    def _get_envelope_data(self, data: dict) -> dict:
        envelope = None
        if (
            data.get("method") is not None and
            data["method"] == "receive" and
            data.get("params") is not None and
            data["params"].get("envelope") is not None
        ):
            envelope = data["params"]["envelope"]
        return envelope

    def _get_basic_formated_data(self, data: dict) -> schemas.DataFormated:
        return schemas.DataFormated(
            id=str(uuid4()),
            user=schemas.User(
                nickname=data.get("sourceName"),
                phone=data.get("sourceNumber")
            ),
            sent_at=data.get("timestamp")
        )

    def _get_sync_message_envelope_if_allowed(self, envelope) -> dict:
        if (
            envelope.get("syncMessage") is not None and
            envelope["syncMessage"].get("sentMessage") is not None and
            is_allow_to_execute_self_send()
        ):
            return envelope["syncMessage"]["sentMessage"]
        return envelope

    def _get_message_formated_data(self, data: dict) -> schemas.Message | None:
        if data is not None and data.get("message") is not None:
            return schemas.Message(
                text=data.get("message"),
                quote=self._get_quote_formated_data(data.get("quote")),
                mentions=self._get_mentions_formated_data(data.get("mentions"))
            )
        return None

    def _get_quote_formated_data(self, data: dict) -> schemas.QuotedMessage | None:
        if data is not None:
            return schemas.QuotedMessage(
                text=data.get("text"),
                author=schemas.User(
                    nickname=data.get("author"),
                    phone=data.get("authorNumber")
                ),
                mentions=self._get_mentions_formated_data(data.get("mentions"))
            )
        return None

    def _get_mentions_formated_data(self, data: dict) -> List[schemas.Mention] | None:
        mentions = None
        if data is not None and len(data) > 0:
            mentions = List()
            for item in data:
                mentions.append(
                    schemas.Mention(
                        user=schemas.User(
                            nickname=item.get("name"),
                            phone=data.get("number")
                        ),
                        start=data.get("start"),
                        length=data.get("length")
                    )
                )
        return mentions

    def _get_reaction_formated_data(self, data: dict) -> schemas.Reaction | None:
        if data is not None and data.get("reaction") is not None:
            data = data.get("reaction")
            return schemas.Reaction(
                reaction=data.get("emoji"),
                target_author=schemas.User(
                    nickname=data.get("targetAuthor"),
                    phone=data.get("targetAuthorNumber")
                ),
                target_sent_at=data.get("targetSentTimestamp")
            )
        return None

    def _get_attachments_formated_data(
        self, data: dict
    ) -> List[schemas.AttachmentData] | None:

        attachments = None
        if (
            data is not None and data.get("attachments") is not None and 
            len(data.get("attachments")) > 0
        ):
            attachments = List()
            for item in data.get("attachments"):
                attachments.append(
                    schemas.AttachmentData(
                        content_type=item.get("contentType"),
                        filename=item.get("filename"),
                        size=item.get("size")
                    )
                )
        return attachments
