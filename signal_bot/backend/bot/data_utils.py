from typing import List

from signal_bot.backend.core.config import get_number_map_db
from signal_bot.backend.schemas.data_formated import (
    DataFormated,
    Mention
)

def _get_users_from_mentions_data(mentions: List[Mention] | None) -> List:
    users = list()
    if mentions is not None:
        for mention in mentions:
            users.append(mention.user)
    return users

def enrich_user_data_with_db_name(data: DataFormated) -> DataFormated:
    users = [data.user]
    if data.message is not None:
        if data.message.quote is not None:
            users.append(data.message.quote.author)
            users += _get_users_from_mentions_data(data.message.quote.mentions)

        users += _get_users_from_mentions_data(data.message.mentions)
    if data.reaction is not None:
        users.append(data.reaction.target_author)
    db = get_number_map_db()
    for user in users:
        user.db_name = db.get(user.phone)
    return data
