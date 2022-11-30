from fastapi import Header, Query

from signal_bot.backend.core.security import is_id_token_valid

def get_auth_user(authorization: str = Header()):
    is_id_token_valid(authorization[7:])

async def check_account_number(account: str = Query(description="Number of the phone for the account", regex="^[0-9]*$")):
    return "+" + account