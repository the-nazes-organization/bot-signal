import uuid
from datetime import datetime

import pytest

from app.bot.schema.data_formated import (
    DataFormated,
    Mention,
    Message,
    QuotedMessage,
    User,
)


@pytest.fixture(scope="module")
def user_map_storage(object_storage):
    object_storage.put("+34567890", "pif")
    object_storage.put("+23456789", "paf")
    object_storage.put("+12345678", "pouf")
    object_storage.put("+01234567", "plop")
    return object_storage


@pytest.fixture(
    scope="function",
    params=["basic", "mention", "quote", "quote_men", "mention|quote|quote_men"],
)
def user_oriented_data(request):
    pif = User(nickname="The Pif", phone="+34567890")
    paf = User(nickname="The Paf", phone="+23456789")
    pouf = User(nickname="The Pouf", phone="+12345678")
    plop = User(nickname="The Plop", phone="+01234567")
    data = DataFormated(id=str(uuid.uuid4()), sent_at=datetime.now(), user=pif)
    if request.param != "basic":
        data.message = Message(text="X Here i come!")
        if "mention" in request.param:
            data.message.mentions = [Mention(user=paf, start=0, length=1)]

        if "quote" in request.param:
            data.message.quote = QuotedMessage(text="X Here it is goes!", author=pouf)

            if "quote_men" in request.param:
                data.message.quote.mentions = [Mention(user=plop, start=0, length=1)]

    user_filled = data.copy()
    user_filled.user.db_name = "pif"
    if "mention" in request.param:
        user_filled.message.mentions[0].user.db_name = "paf"
    if "quote" in request.param:
        user_filled.message.quote.author.db_name = "pouf"
        if "quote_men" in request.param:
            user_filled.message.quote.mentions[0].user.db_name = "plop"

    return {"empty": data, "filled": user_filled}
