from random import randrange

from app.bot.chat_client.chatter import ChatterHolder
from app.bot.command import Command
from app.bot.schema.data_formated import DataFormated
from app.config import get_attachment_format_from_files, get_attachments_path


@Command.add("command", "!tiresurmondoigt")
def the_first_joke(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(message="prout", quote_id=data.id)


@Command.add("command", "!help")
def list_command(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(
        message=", ".join([cmd["prefix"] for cmd in Command._command["command"]])
    )


@Command.add("message", condition={"users": ["valentin"]})
def menfou(data: DataFormated):
    if randrange(1, 20) == 20:
        chatter = ChatterHolder.get_chatter()
        chatter.send_message(message="MENFOU", quote_id=data.id)
