import argparse
import logging
import logging.config
from typing import List
from json import JSONDecodeError

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.commands.command import Command
from signal_bot.backend.core.config import (
    get_chatter,
    get_number_map_db,
    get_queue_storage,
)
from signal_bot.backend import schemas
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


###################
###### Utils ######
def _add_db_name_to_user(user: schemas.User):
    db = get_number_map_db()
    user.db_name = db.get(user.phone)

def _get_users_from_mentions_data(mentions: List[schemas.Mention] | None) -> List:
    users = List()
    if mentions is not None:
        for mention in mentions:
            users.append(mention.user)
    return users

def _enrich_user_data(data: schemas.DataFormated):
    users = List()
    users.append(data.user)
    if data.message is not None:
        if data.message.quote is not None:
            users.append(data.message.quote.author)
            users += _get_users_from_mentions_data(data.message.quote.mentions)

        users += _get_users_from_mentions_data(data.message.mentions)
    if data.reaction is not None:
        users.append(data.reaction.target_author)
    map(_add_db_name_to_user, users)
#### End Utils ####
###################


def bot_loop_hole(bot_client: Chatter, command: Command, queue: QueueStorage):
    while True:
        try:
            data = bot_client.read_message()
        except ValueError:
            logger.info("Improper Value read", exc_info=1)
            continue
        if data is None:
            continue

        _enrich_user_data(data)

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
