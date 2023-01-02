import sys

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.commands.command import Command
from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.core.config import get_queue_storage
from signal_bot.backend.core.config import get_chatter
from signal_bot.backend.db.getter import get_name_by_number

# Import all functions to add them to the command with the decorator
from signal_bot.backend.commands.functions import basic  # pylint: disable=unused-import
from signal_bot.backend.commands.functions import openai  # pylint: disable=unused-import

def bot_loop_hole(bot_client: Chatter, command: Command, queue: QueueStorage):
    while True:
        message_dict = bot_client.read_message()

        if (message_dict["type"] == "message"):

            queue.put(message_dict)
            command.handle_message(
                message=message_dict["params"]["dataMessage"]["message"],
                user=get_name_by_number(message_dict["params"]["sourceNumber"]),
            )

            if message_dict["params"]["dataMessage"].get("attachments") is not None:
                command.handle_attachements(
                    user=get_name_by_number(message_dict["params"]["sourceNumber"]),
                    attachements=message_dict["params"]["dataMessage"]["attachments"]
                )

        elif (message_dict["type"] == "typing"):
            command.handle_typing(
                user=get_name_by_number(message_dict["params"]["sourceNumber"])
            )


commander = Command()
queue_storage = get_queue_storage()
chatter = get_chatter(queue=queue_storage)
bot_loop_hole(chatter, commander, queue_storage)
