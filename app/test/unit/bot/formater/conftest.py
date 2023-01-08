import pytest

from app.bot.chat_client.clients.signal.formaters.jsonrpc import JsonRpcFormater

@pytest.fixture(params=["group_id", "recipient"])
def formater(request):
    receiver = {
        "group_id" : "dhwq98hwqoud1092u",
        "recipient": "+0921830921"
    }
    return JsonRpcFormater(
        account="+23819239",
        receiver_type=request.param,
        receiver=receiver.get(request.param)
    )