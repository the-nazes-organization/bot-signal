import json
import sys
from signal_bot.backend.bot.chat_client.chatter import Chatter
from signal_bot.backend.bot.chat_client.clients.signal_chatter import SignalChatter
from signal_bot.backend.commands.command import Command

# Import all functions to add them to the command with the decorator
from signal_bot.backend.commands.functions import basic #pylint: disable=unused-import
from signal_bot.backend.commands.functions import openai #pylint: disable=unused-import


def bot_loop_hole(bot_client: Chatter, command: Command):
    while True:
        message_dict = bot_client.read_message()

        if (
            message_dict["type"] == "message"
            and message_dict["params"].get("dataMessage") is not None
        ):
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

def get_properties() -> dict:
    properties_json = sys.stdin.read()
    return json.loads(properties_json)

def get_chatter() -> Chatter:
    properties = get_properties()
    return SignalChatter(**properties)

chatter = get_chatter()
commander = Command()
bot_loop_hole(chatter, commander)
