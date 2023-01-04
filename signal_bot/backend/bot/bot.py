import argparse
import logging
import logging.config

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.commands.command import Command
from signal_bot.backend.core.config import (
    get_chatter,
    get_number_map_db,
    get_queue_storage,
)
from signal_bot.backend.core.logger_conf import LOGGING
from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.schemas.bot import BotProperties

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

# Import all functions to add them to the command with the decorator
from signal_bot.backend.commands import functions

parser = argparse.ArgumentParser(description="Signal bot")
parser.add_argument(
    "-a", "--account", help="Account to use if format +33642424242", type=str
)
parser.add_argument(
    "-rt",
    "--receiver_type",
    help="Type of receiver",
    choices=["group_id", "recipient"],
)
parser.add_argument("-r", "--receiver", help="Receiver to use", type=str)
args = parser.parse_args()


def get_name_by_number(number: str):
    db = get_number_map_db()
    return db.get(number)


def bot_loop_hole(bot_client: Chatter, command: Command, queue: QueueStorage):
    while True:
        message_dict = bot_client.read_message()

        if message_dict["type"] == "message":

            if message_dict["params"]["dataMessage"]["message"] is not None:
                queue.put(message_dict)
                command.handle_message(
                    message=message_dict["params"]["dataMessage"]["message"],
                    user=get_name_by_number(message_dict["params"]["sourceNumber"]),
                )

            if message_dict["params"]["dataMessage"].get("attachments") is not None:
                command.handle_attachements(
                    user=get_name_by_number(message_dict["params"]["sourceNumber"]),
                    attachements=message_dict["params"]["dataMessage"]["attachments"],
                )

        elif message_dict["type"] == "typing":
            command.handle_typing(
                user=get_name_by_number(message_dict["params"]["sourceNumber"])
            )


if __name__ == "__main__":
    properties = BotProperties(
        account=args.account, receiver_type=args.receiver_type, receiver=args.receiver
    )
    commander = Command()
    queue_storage = get_queue_storage()
    chatter = get_chatter(queue=queue_storage, properties=properties)

    ChatterHolder(chatter)
    bot_loop_hole(chatter, commander, queue_storage)
