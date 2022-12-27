import sys

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.commands.command import Command
from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.core.config import get_queue_storage
from signal_bot.backend.core.config import get_chatter

# Import all functions to add them to the command with the decorator
from signal_bot.backend.commands.functions import basic  # pylint: disable=unused-import
from signal_bot.backend.commands.functions import openai  # pylint: disable=unused-import


def bot_loop_hole(bot_client: Chatter, command: Command, queue: QueueStorage):
    while True:
        message_dict = bot_client.read_message()

        if (
            message_dict["type"] == "message"
            and message_dict["params"].get("dataMessage") is not None
        ):
            # save message in queue
            queue.put(message_dict)
            command.handle_message(
                message=message_dict["params"]["dataMessage"]["message"],
                user=message_dict["params"]["sourceNumber"],
            )

        # DEV self sending
        if (
            message_dict.get("params") is not None
            and message_dict["params"].get("syncMessage") is not None
            and message_dict["params"]["syncMessage"].get("sentMessage") is not None
            and message_dict["params"]["syncMessage"]["sentMessage"].get("message")
            is not None
        ):
            sys.stdout.write(
                "DEV Handling message"
                f" {message_dict['params']['syncMessage']['sentMessage']['message']}\n"
            )
            command.handle_message(
                message=message_dict["params"]["syncMessage"]["sentMessage"]["message"],
                user=message_dict["params"]["sourceNumber"],
            )


chatter = get_chatter()
commander = Command()
queue_storage = get_queue_storage()
bot_loop_hole(chatter, commander, queue_storage)
