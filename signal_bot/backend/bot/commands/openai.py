from signal_bot.backend.core.command import Command
from signal_bot.backend.bot.socket_chatter import SocketChatter
from signal_bot.backend.core.config import get_settings

import openai

MAX_TOKENS_COMPLETION_USAGE = 1000

@Command.add("command", "!gpt")
def ignorant_ai(message, user):
    settings = get_settings()
    openai.api_key = settings.OPENAI_API_KEY
    chatter = SocketChatter()

    response = openai.Completion.create(model="text-davinci-003", prompt=message, max_tokens=MAX_TOKENS_COMPLETION_USAGE)
    chatter.send_message(f'"{response.choices[0].text}"')
