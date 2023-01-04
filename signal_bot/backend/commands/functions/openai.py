import logging
import os

import openai

from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.commands.command import Command
from signal_bot.backend.core.config import get_number_map_db, get_settings

# pylint: disable=unused-argument
logger = logging.getLogger(__name__)


@Command.add("command", "🤖")
def ignorant_ai(message, user):
    chatter = ChatterHolder.get_chatter()
    chatter.send_typing()
    db_obj = get_number_map_db()
    base_prompt = load_base_prompt("ignorant_ai_prompt")
    name_mapping = db_obj.get_all()
    prompt = create_prompt_context(
        chatter=chatter, name_mapping=name_mapping, base_prompt=base_prompt
    )
    response = get_openai_prediction(prompt=prompt)
    chatter.send_message(response)


@Command.add("command", "🤖👿")
def evil_ai(message, user):
    chatter = ChatterHolder.get_chatter()
    chatter.send_typing()
    db_obj = get_number_map_db()
    name_mapping = db_obj.get_all()
    base_prompt = load_base_prompt("evil_ai_prompt")
    prompt = create_prompt_context(
        chatter=chatter, name_mapping=name_mapping, base_prompt=base_prompt
    )
    response = get_openai_prediction(prompt=prompt)
    chatter.send_message(response)


@Command.add("command", "🖌️")
def create_img_from_text(message, user):
    chatter = ChatterHolder.get_chatter()
    chatter.send_typing()
    settings = get_settings()
    openai.api_key = settings.OPENAI_API_KEY
    response = openai.Image.create(prompt=message, n=4, response_format="b64_json")
    attachments = [
        "data:image/png;base64," + data["b64_json"] for data in response.data
    ]
    chatter.send_message(message="", attachments=attachments)


def load_base_prompt(prompt):
    settings = get_settings()
    path_mappping = {
        "ignorant_ai_prompt": settings.OPENAI_BASE_PROMPT_PATH,
        "evil_ai_prompt": settings.OPENAI_BASE_PROMPT_EVIL_PATH,
    }
    prompt_path = os.path.join(settings.VOLUME_PATH, path_mappping[prompt])
    try:
        with open(prompt_path, "r", encoding="utf-8") as open_file:
            base_prompt = open_file.read()
    except FileNotFoundError:
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


def create_prompt_context(chatter, name_mapping, base_prompt=""):
    settings = get_settings()
    history = chatter.get_history(int(settings.OPENAI_HISTORY_LENGTH))
    history.reverse()
    chat = ""
    for message_dict in history:
        message = get_message_from_dict(message_dict)
        user_phone = get_user_from_dict(message_dict)
        user_name = name_mapping.get(user_phone)
        chat += f"{user_name}: {message}\n"
    prompt_context = base_prompt.replace("INSERT_CHAT_HERE", chat)
    return prompt_context


def get_message_from_dict(message_dict):
    if "dataMessage" in message_dict["params"]:
        message = message_dict["params"]["dataMessage"]["message"]
    elif "message" in message_dict["params"]:
        message = message_dict["params"]["message"]
    else:
        message = ""
    return message


def get_user_from_dict(message_dict):
    if "sourceNumber" in message_dict["params"]:
        user = message_dict["params"]["sourceNumber"]
    elif "account" in message_dict["params"]:
        user = message_dict["params"]["account"]
    else:
        user = ""
    return user
