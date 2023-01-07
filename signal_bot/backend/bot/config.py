from base64 import b64encode
from typing import List
import mimetypes

from signal_bot.backend.core.config import get_settings

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.clients.facebook_chatter import FacebookChatter
from signal_bot.backend.bot.chat_client.clients.signal_chatter import SignalChatter
from signal_bot.backend.bot.chat_client.formater import MessageFormater
from signal_bot.backend.bot.chat_client.formaters.signal_formater import JsonRpcFormater

from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.db.queue_storage_provider.deque_storage import DequeStorage


def get_formater(properties) -> MessageFormater:
    return JsonRpcFormater(
        account=properties.account,
        receiver_type=properties.receiver_type,
        receiver=properties.receiver,
    )


def get_chatter(queue, properties) -> Chatter:
    settings = get_settings()
    mapping = {
        "signal": SignalChatter,
        "facebook": FacebookChatter,
    }
    formater = get_formater(properties)
    return mapping[settings.CHATTER_CLIENT](
        queue=queue, formater=formater, socket_file=settings.SOCKET_FILE
    )

def get_queue_storage() -> QueueStorage:
    settings = get_settings()
    mapping = {
        "deque": DequeStorage,
    }
    return mapping[settings.QUEUE_STORAGE_PROVIDER](settings.QUEUE_STORAGE_MAXLEN)

def get_attachment_format_from_files(files_path: List[str]) -> List[str]:
    attachments = list()
    for file_path in files_path:
        with open(file_path, "r") as attachment:
            encoded_string = b64encode(attachment.read())
            data_type = mimetypes.guess_type(file_path)
            attachments.append(f"data:{data_type};base64,{encoded_string}")
    return attachments