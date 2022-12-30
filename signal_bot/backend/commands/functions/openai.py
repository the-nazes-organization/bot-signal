import openai
import logging
import os

from signal_bot.backend.commands.command import Command
from signal_bot.backend.bot import bot
from signal_bot.backend.core.config import get_settings

#pylint: disable=unused-argument
logger = logging.getLogger(__name__)

@Command.add("command", "🤖")
def ignorant_ai(message, user):
    base_prompt = load_base_prompt("ignorant_ai")
    prompt = create_prompt_context(base_prompt=base_prompt)
    response = get_openai_prediction(prompt=prompt)
    bot.chatter.send_message(f'"{response.choices[0].text}"')

@Command.add("command", "🤖👿")
def evil_ai(message, user):
    base_prompt = load_base_prompt("evil_ai")
    prompt = create_prompt_context(base_prompt=base_prompt)
    response = get_openai_prediction(prompt=prompt)
    bot.chatter.send_message(f'"{response.choices[0].text}"')

def load_base_prompt(prompt):
    settings = get_settings()
    path_mappping = {
        "ignorant_ai": settings.OPENAI_BASE_PROMPT,
        "evil_ai": settings.OPENAI_BASE_PROMPT_EVIL,
    }
    prompt_path = os.path(settings.VOLUME_PATH, path_mappping[prompt])
    try:
        with open(prompt_path, "r") as open_file:
            base_prompt = open_file.read()
    except:
        logger.error("Couldn´t load base prompt in path : %s", prompt_path)
        base_prompt = ""
    return base_prompt

def get_openai_prediction(prompt):
    settings = get_settings()
    openai.api_key = settings.OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=int(settings.OPENAI_COMPLETION_MAX_TOKEN),
    )
    return response

def create_prompt_context(base_prompt=""):
    settings = get_settings()
    history = bot.chatter.get_history(int(settings.OPENAI_HISTORY_LENGTH))
    history.reverse()
    prompt_context = base_prompt
    for message_dict in history:
        message=message_dict["params"]["dataMessage"]["message"]
        user=message_dict["params"]["sourceNumber"]
        prompt_context += f"{user}: {message}\n"
    return prompt_context
