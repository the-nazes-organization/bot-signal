from typing import List
from datetime import datetime

from signal_bot.backend.bot.chat_client.chatter_holder import ChatterHolder
from signal_bot.backend.bot.chat_client.chatter import Chatter

from signal_bot.backend.commands.command import Command

# Import all functions to add them to the command with the decorator
from signal_bot.backend.commands import functions


class TestChatter(Chatter):
    def __init__(self, queue) -> None:
        self.queue = queue
        self.results = {}

    def read_message(self):
        return super().read_message()

    def send_message(
        self,
        message: str | None = None,
        attachments: List[str] | None = None,
        quote_id: str | None = None
    ):
        if message is None and attachments is None and quote_id is None:
            raise NotImplementedError("Send message without params")
        self.results["send_message"] = {
                "message":message,
                "attachments":attachments,
                "quote_id":quote_id
            }
    
    def send_reaction(self, emoji: str, target_author: str, target_sent_at: datetime):
        self.results["send_reaction"] = {
            "emoji":emoji,
            "target_author":target_author,
            "target_sent_at":target_sent_at
        }
    
    def send_typing(self):
        self.results["send_typing"] = "ON"
    
    def get_history(self, nb_messages: int = 10):
        return self.queue.get_n_last(nb_messages)


def get_chatter(queue) -> TestChatter:
    if (chatter := ChatterHolder.get_chatter()) is None:
        chatter = TestChatter(queue)
        ChatterHolder(chatter)
    return chatter


def test_commands_with_message(queue_storage, basic_message_data_formated):
    data = basic_message_data_formated

    chatter = get_chatter(queue_storage)
    cmd = Command()

    queue_storage.put(data)
    cmd.handle_message(data)

    print(chatter.results)


def test_commands_with_typing(queue_storage, typing_data_formated):
    data = typing_data_formated

    chatter = get_chatter(queue_storage)
    cmd = Command()

    cmd.handle_typing(data)

    print(chatter.results)


def test_commands_with_reaction(queue_storage, reaction_data_formated):
    data = reaction_data_formated

    chatter = get_chatter(queue_storage)
    cmd = Command()

    cmd.handle_reaction(data)

    print(chatter.results)


def test_commands_with_attachments(queue_storage, attachments_data_formated):
    data = attachments_data_formated

    chatter = get_chatter(queue_storage)
    cmd = Command()

    cmd.handle_attachments(data)

    print(chatter.results)