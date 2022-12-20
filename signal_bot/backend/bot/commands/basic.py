from signal_bot.backend.core.command import Command
from signal_bot.backend.bot.socket_chatter import SocketChatter

@Command.add("command", "!tiresurmondoigt")
def the_first_joke(message, user):
    chatter = SocketChatter()
    chatter.send_message("prout")

@Command.add("command", "!help")
def help(message, user):
    chatter = SocketChatter()
    chatter.send_message("!tiresurmondoigt, !gpt 'prompt'")

@Command.add("message", condition={"users":["+33627691798"]})
def menfou(message, user):
    if len(message) > 20:
        chatter = SocketChatter()
        chatter.send_message("MENFOU")