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


@Command.add("reaction")
def reacted(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(message="Worked reac")


@Command.add("command", "!react")
def reacttomessage(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_reaction("👯‍♂️", data.user.phone, data.sent_at)


@Command.add("command", "!quoteme")
def quoteme(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(message="I quote the big buffoon", quote_id=data.id)


@Command.add("typing")
def istyping(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(message=f"@@{data.user.db_name} is typing")


@Command.add("command", "!buffoon")
def sendbuffoon(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_message(
        attachments=get_attachment_format_from_files(
            [get_attachments_path() + "/" + "William_Merritt_Chase_Keying_up.jpg"]
        )
    )
