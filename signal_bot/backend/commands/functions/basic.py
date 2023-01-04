from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.commands.command import Command


@Command.add("command", "!tiresurmondoigt")
def the_first_joke(message, user):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message("prout")


@Command.add("command", "!help")
def list_command(message, user):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(
        ", ".join(
            [cmd["prefix"] for cmd in Command._command["command"]]
        )
    )


@Command.add("message", condition={"users": ["valentin"]})
def menfou(message, user):
    chatter = ChatterHolder.get_chatter()
    if len(message) > 20:
        chatter.send_message("MENFOU")
