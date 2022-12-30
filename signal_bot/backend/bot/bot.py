import sys
import argparse
import logging
import logging.config

from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.commands.command import Command
from signal_bot.backend.db.queue_storage import QueueStorage
from signal_bot.backend.core.config import get_queue_storage
from signal_bot.backend.core.config import get_chatter
from signal_bot.backend.db.getter import get_number_by_name
from signal_bot.backend.core.logger_conf import LOGGING
from signal_bot.backend.schemas.bot import BotProperties

# Import all functions to add them to the command with the decorator
from signal_bot.backend.commands.functions import basic  # pylint: disable=unused-import
from signal_bot.backend.commands.functions import openai  # pylint: disable=unused-import


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(description="Signal bot")
parser.add_argument(
    "-a", "--account", help="Account to use if format +33642424242", type=str, default="+33642424242"
)
parser.add_argument(
    "-rt", "--receiver_type", help="Type of receiver", type=str, choices=['group_id', 'recipient'], default="group_id"
)
parser.add_argument(
    "-r", "--receiver", help="Receiver to use", type=str, default="group_id"
)
args = parser.parse_args()


def bot_loop_hole(bot_client: Chatter, command: Command, queue: QueueStorage):
    while True:
        message_dict = bot_client.read_message()
        logger.info(msg=f"Received message: {message_dict}")

        if (
            message_dict["type"] == "message"
            and message_dict["params"].get("dataMessage") is not None
        ):
            queue.put(message_dict)
            command.handle_message(
                message=message_dict["params"]["dataMessage"]["message"],
                user=get_number_by_name(message_dict["params"]["sourceNumber"]),
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


properties = BotProperties(
    account=args.account,
    receiver_type=args.receiver_type,
    receiver=args.receiver
)
commander = Command()
queue_storage = get_queue_storage()
chatter = get_chatter(queue=queue_storage, properties=properties)
bot_loop_hole(chatter, commander, queue_storage)
