from random import randrange

from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.commands.command import Command
from signal_bot.backend import schemas


@Command.add("command", "!tiresurmondoigt")
def the_first_joke(data: schemas.DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(message="prout")


@Command.add("command", "!help")
def list_command(data: schemas.DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(
        message=", ".join(
            [cmd["prefix"] for cmd in Command._command["command"]]
        )
    )


@Command.add("message", condition={"users": ["valentin"]})
def menfou(data: schemas.DataFormated):
    chatter = ChatterHolder.get_chatter()
    if randrange(1, 20) == 20:
        chatter.send_message(message="MENFOU", quote_id=data.id)
