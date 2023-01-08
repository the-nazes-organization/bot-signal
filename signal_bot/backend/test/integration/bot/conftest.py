import pytest

from datetime import datetime
from random import randrange
import uuid
import time

from signal_bot.backend.schemas.data_formated import (
    DataFormated,
    User,
    Message,
    Typing,
    Reaction,
    AttachmentData
)


def get_random_elem(list):
    return list[randrange(0, len(list))]

def get_db_name_to_test():
    names = ["michel", "val", "rom", "poireau", "max", "cochon", "orange", "jo", "ane"]
    return get_random_elem(names)

def get_random_user():
    return User(
            nickname=f"Tester {randrange(0, 50)}",
            phone=f"+{randrange(100000000, 999999999)}",
            db_name=get_db_name_to_test()
        )

def get_random_datetime() -> datetime:
    return datetime.fromtimestamp(time.time() - float(randrange(100, 1000)))

def get_random_data_formated() -> DataFormated:
    return DataFormated(
        id=str(uuid.uuid4()),
        sent_at=get_random_datetime(),
        user=get_random_user()
    )


def get_test_message():
    return ["!hello", "!help", "bonjour", "pi pa pou je vais en foret"]

@pytest.fixture(params=get_test_message())
def basic_message_data_formated(request):
    data = get_random_data_formated()
    data.message = Message(
        text=request.param
    )
    return data


@pytest.fixture(params=["STARTED", "STOPPED"])
def typing_data_formated(request):
    data = get_random_data_formated()
    data.typing = Typing(
        status=request.param
    )
    return data


def get_test_reactions():
    return ["🖕", "👍", "👎"]

@pytest.fixture(params=get_test_reactions())
def reaction_data_formated(request):
    data = get_random_data_formated()
    data.reaction = Reaction(
        reaction=request.param,
        target_author=get_random_user(),
        sent_at=get_random_datetime()
    )
    return data


def get_test_attachments():
    return ["poire.txt", "dinosaure.png"]

@pytest.fixture(params=get_test_attachments())
def attachments_data_formated(request):
    data = get_random_data_formated()
    data.attachments = [
        AttachmentData(
            content_type="file",
            filename=request.param,
            size=randrange(100000, 1000000)
        )
    ]
