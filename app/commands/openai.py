import logging
import os
from typing import List

import openai

from app.bot.schema.data_formated import DataFormated
from app.bot.chat_client.chatter import ChatterHolder
from app.bot.command import Command
from app.config import get_settings

logger = logging.getLogger(__name__)


@Command.add("command", "🤖")
def ignorant_ai(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_typing()

    base_prompt = load_base_prompt("ignorant_ai_prompt")
    prompt = create_prompt_context(
        chatter=chatter, base_prompt=base_prompt
    )
    response = get_openai_prediction(prompt=prompt)
    chatter.send_message(message=response)


@Command.add("command", "🤖👿")
def evil_ai(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_typing()
    #si message start new_personality: 
        

    base_prompt = load_base_prompt("evil_ai_prompt")
    prompt = create_prompt_context(
        chatter=chatter, base_prompt=base_prompt
    )
    response = get_openai_prediction(prompt=prompt)
    chatter.send_message(message=response)


@Command.add("command", "🖌️")
def create_img_from_text(data: DataFormated):
    chatter = ChatterHolder.get_chatter()
    chatter.send_typing()
    settings = get_settings()
    openai.api_key = settings.OPENAI_API_KEY
    response = openai.Image.create(
        prompt=data.message.text, n=4, response_format="b64_json"
    )
    attachments = [
        "data:image/png;base64," + data["b64_json"] for data in response.data
    ]
    chatter.send_message(attachments=attachments)


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


def create_prompt_context(chatter, base_prompt=""):
    settings = get_settings()
    history: List[DataFormated] = chatter.get_history(
        int(settings.OPENAI_HISTORY_LENGTH)
    )
    history.reverse()
    chat = ""
    for message_data in history:
        message = message_data.message.text
        user_name = message_data.user.db_name
        chat += f"{user_name}: {message}\n"
    prompt_context = base_prompt.replace("INSERT_CHAT_HERE", chat)
    return prompt_context
