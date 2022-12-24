import json
import sys
from signal_bot.backend.bot.socket_chatter import SocketChatter
from signal_bot.backend.core.command import Command


def bot_loop_hole(chatter: SocketChatter, commander: Command):
    while True:
        message_dict = chatter.read_message()

        if (
            message_dict["type"] == "message"
            and message_dict["params"].get("dataMessage") is not None
        ):
            commander.handle_message(
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
            commander.handle_message(
                message=message_dict["params"]["syncMessage"]["sentMessage"]["message"],
                user=message_dict["params"]["sourceNumber"],
            )


def get_properties() -> dict:
    properties_json = sys.stdin.read()
    return json.loads(properties_json)

def main():
    properties = get_properties()
    chatter = SocketChatter(**properties)
    commander = Command()
    bot_loop_hole(chatter, commander)

if __name__ == "__main__":
    main()
