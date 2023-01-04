from signal_bot.backend.bot.chat_client.chatter import Chatter


class ChatterHolder:
    _instance = None

    def __init__(self, chatter: Chatter) -> None:
        if self._instance is None:
            self.__class__._instance = chatter

    @classmethod
    def get_chatter(cls) -> Chatter:
        return cls._instance
