import json

from signal_bot.backend.schemas import BotProperties


class SignalBot:
    def __init__(self, properties: str) -> None:
        properties_dict = json.loads(properties)
        self.properties = BotProperties(**properties_dict)
