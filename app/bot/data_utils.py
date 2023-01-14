from typing import List

from app.bot.schema.data_formated import DataFormated, Mention
from app.db.object_storage import ObjectStorage


def _get_users_from_mentions_data(mentions: List[Mention] | None) -> List:
    users = list()
    if mentions:
        for mention in mentions:
            users.append(mention.user)
    return users


def enrich_user_data_with_db_name(
    data: DataFormated, user_db: ObjectStorage
) -> DataFormated:
    users = [data.user]
    if data.message:
        if data.message.quote:
            users.append(data.message.quote.author)
            users += _get_users_from_mentions_data(data.message.quote.mentions)

        users += _get_users_from_mentions_data(data.message.mentions)
    if data.reaction:
        users.append(data.reaction.target_author)
    for user in users:
        user.db_name = user_db.get(user.phone)
    return data
