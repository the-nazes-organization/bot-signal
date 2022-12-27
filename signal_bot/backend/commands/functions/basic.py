from signal_bot.backend.bot.bot import chatter
from signal_bot.backend.commands.command import Command

#pylint: disable=unused-argument

@Command.add("command", "!tiresurmondoigt")
def the_first_joke(message, user):
    chatter.send_message("prout")

@Command.add("command", "!help")
def list_command(message, user):
    chatter.send_message(
        ", ".join([cmd["prefix"] for cmd in Command._command["command"]]) #pylint: disable=protected-access
    )

@Command.add("message", condition={"users": ["+33627691798"]})
def menfou(message, user):
    if len(message) > 20:
        chatter.send_message("MENFOU")
