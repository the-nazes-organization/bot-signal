import argparse
import logging
import logging.config

from app.bot.chat_client.chatter import Chatter, ChatterHolder
from app.config import get_chatter, get_queue_storage, get_user_db
from app.bot.data_utils import enrich_user_data_with_db_name
from app.bot.command import Command
from app.logger_conf import LOGGING
from app.db.queue_storage import QueueStorage
from app.backend.schemas.bot import BotProperties
from app.bot.schema.data_formated import DataFormated

# Import all functions to add them to the command with the decorator
from app import commands


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


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
            logger.error("Improper Value read", exc_info=1)
            continue
        if data is None:
            continue

        user_db = get_user_db()
        data = enrich_user_data_with_db_name(data, user_db=user_db)

        if data.message:
            queue.put(data)
            command.handle_message(data)

        if data.typing:
            command.handle_typing(data)
        
        if data.reaction:
            command.handle_reaction(data)
        
        if data.attachments:
            command.handle_attachements(data)

def main():
    properties = BotProperties(
        account=args.account, receiver_type=args.receiver_type, receiver=args.receiver
    )
    commander = Command()
    queue_storage = get_queue_storage()
    annuaire = get_user_db()
    chatter = get_chatter(queue=queue_storage, properties=properties, annuaire=annuaire)

    ChatterHolder(chatter)
    bot_loop_hole(chatter, commander, queue_storage)

if __name__ == "__main__":
    main()
