import openai

from signal_bot.backend.commands.command import Command
from signal_bot.backend.bot.bot import chatter
from signal_bot.backend.core.config import get_settings

#pylint: disable=unused-argument

@Command.add("command", "🤖")
def ignorant_ai(message, user):
    settings = get_settings()
    base_prompt = settings.OPENAI_BASE_PROMPT
    prompt = create_prompt_context(base_prompt=base_prompt)
    response = get_openai_prediction(prompt=prompt)
    chatter.send_message(f'"{response.choices[0].text}"')

@Command.add("command", "🤖😈")
def evil_ai(message, user):
    settings = get_settings()
    base_prompt = settings.OPENAI_BASE_PROMPT_EVIL
    prompt = create_prompt_context(base_prompt=base_prompt)
    response = get_openai_prediction(prompt=prompt)
    chatter.send_message(f'"{response.choices[0].text}"')

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
    history = chatter.get_history(20)
    prompt_context = base_prompt
    for message_dict in history.reverse():
        message=message_dict["params"]["dataMessage"]["message"]
        user=message_dict["params"]["sourceNumber"]
        prompt_context += f"{user}: {message}\n"
    return prompt_context
