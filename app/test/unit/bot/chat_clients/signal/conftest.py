import os

import pytest

from app.bot.chat_client.clients.signal.formaters.jsonrpc import JsonRpcFormater


@pytest.fixture(scope="module", params=["group_id"])
def formater(request):
    receiver = {"group_id": "dhwq98hwqoud1092u", "recipient": "+03294832"}
    return JsonRpcFormater(
        account="+23819239",
        receiver_type=request.param,
        receiver=receiver.get(request.param),
    )


@pytest.fixture(scope="module")
def phonebook(object_storage):
    object_storage.put("+309213", "popo")
    object_storage.put("+309999", "pipi")
    object_storage.put("+023923", "po")
    return object_storage.get_all()


@pytest.fixture(scope="module")
def raw_data(request):
    if hasattr(request, "param"):
        data_file = request.param
    else:
        data_file = "message"

    fd = open(os.path.join("app/test/data", "raw_" + data_file + ".json"))
    data = fd.read()
    fd.close()
    return data
