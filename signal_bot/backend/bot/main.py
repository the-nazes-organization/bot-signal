import json
import sys
from signal_bot.backend.bot.socket_chatter import SocketChatter
from signal_bot.backend.bot import commands
from signal_bot.backend.core.command import Command

def bot_loop_hole(chatter: SocketChatter, commander: Command):
    while True:
        message_dict = chatter.read_message()

        if message_dict["type"] == "message":
            if message_dict["params"].get("envelope") is not None\
            and message_dict["params"]["envelope"].get("dataMessage") is not None\
            and message_dict["params"]["envelope"]["dataMessage"].get("message") is not None:
                commander.handle_message(
                    message=message_dict["params"]["envelope"]["dataMessage"]["message"],
                    user=message_dict["params"]["envelope"]["sourceNumber"]
                )
            
            #DEV self sending
            # if message_dict["params"].get("syncMessage") is not None\
            # and message_dict["params"]["syncMessage"].get("sentMessage") is not None\
            # and message_dict["params"]["syncMessage"]["sentMessage"].get("message") is not None:
            #     sys.stdout.write(f"DEV Handling message {message_dict['params']['syncMessage']['sentMessage']['message']}\n")
            #     commander.handle_message(
            #         message=message_dict["params"]["syncMessage"]["sentMessage"]["message"],
            #         user=message_dict["params"]["sourceNumber"]
            #     )


def get_properties() -> dict:
    properties_json = sys.stdin.read()
    return json.loads(properties_json)

if __name__ == "__main__":
    properties = get_properties()

    chatter = SocketChatter(**properties)
    commander = Command()
    bot_loop_hole(chatter, commander)
