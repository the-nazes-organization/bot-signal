import openai
import logging
import os

from signal_bot.backend.commands.command import Command
from signal_bot.backend.bot import bot
from signal_bot.backend.core.config import get_settings
from signal_bot.backend.db.getter import get_number_map_db

#pylint: disable=unused-argument
logger = logging.getLogger(__name__)

@Command.add("command", "🤖")
def ignorant_ai(message, user):
    db_obj = get_number_map_db()
    base_prompt = load_base_prompt("ignorant_ai_prompt")
    name_mapping = db_obj.get_all()
    prompt = create_prompt_context(name_mapping=name_mapping, base_prompt=base_prompt)
    response = get_openai_prediction(prompt=prompt)
    bot.chatter.send_message(response)

@Command.add("command", "🤖👿")
def evil_ai(message, user):
    db_obj = get_number_map_db()
    name_mapping = db_obj.get_all()
    base_prompt = load_base_prompt("evil_ai_prompt")
    prompt = create_prompt_context(name_mapping=name_mapping, base_prompt=base_prompt)
    response = get_openai_prediction(prompt=prompt)
    bot.chatter.send_message(response)

def load_base_prompt(prompt):
    settings = get_settings()
    path_mappping = {
        "ignorant_ai_prompt": settings.OPENAI_BASE_PROMPT_PATH,
        "evil_ai_prompt": settings.OPENAI_BASE_PROMPT_EVIL_PATH,
    }
    prompt_path = os.path.join(settings.VOLUME_PATH, path_mappping[prompt])
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
    return response.choices[0].text.strip('"')


def create_prompt_context(name_mapping, base_prompt=""):
    settings = get_settings()
    history = bot.chatter.get_history(int(settings.OPENAI_HISTORY_LENGTH))
    history.reverse()
    chat = ""
    for message_dict in history:
        message=message_dict["params"]["syncMessage"]["sentMessage"]["message"]
        # message=message_dict["params"]["dataMessage"]["message"]
        user_phone=message_dict["params"]["sourceNumber"]
        user_name=find_name_by_number(user_phone, name_mapping)
        chat += f"{user_name}: {message}\n"
    prompt_context = base_prompt.replace("INSERT_CHAT_HERE", chat)
    return prompt_context

def find_name_by_number(number, name_mapping):
    for key, value in name_mapping.items():
        if value == number:
            return key
    return number