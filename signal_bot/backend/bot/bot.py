import argparse
import logging
import logging.config

from signal_bot.backend.bot.config import (
    get_queue_storage,
    get_chatter
)
from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.bot.chat_client.chatter import Chatter

from signal_bot.backend.bot.data_utils import enrich_user_data_with_db_name

from signal_bot.backend.commands.command import Command
from signal_bot.backend.core.logger_conf import LOGGING

from signal_bot.backend.db.queue_storage import QueueStorage

from signal_bot.backend.schemas.data_formated import DataFormated
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


def bot_loop_hole(bot_client: Chatter, command: Command, queue: QueueStorage):
    while True:
        try:
            data: DataFormated = bot_client.read_message()
        except ValueError:
            logger.info("Improper Value read", exc_info=1)
            continue
        if data is None:
            continue

        data = enrich_user_data_with_db_name(data)

        if data.message is not None:
            queue.put(data)
            command.handle_message(data)

        if data.typing is not None:
            command.handle_typing(data)
        
        if data.reaction is not None:
            command.handle_reaction(data)
        
        if data.attachments is not None:
            command.handle_attachements(data)


if __name__ == "__main__":
    properties = BotProperties(
        account=args.account, receiver_type=args.receiver_type, receiver=args.receiver
    )
    commander = Command()
    queue_storage = get_queue_storage()
    chatter = get_chatter(queue=queue_storage, properties=properties)

    ChatterHolder(chatter)
    bot_loop_hole(chatter, commander, queue_storage)
