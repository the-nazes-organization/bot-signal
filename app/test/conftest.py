import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.backend.api.main import app
from app.db.object_storage_provider.fs_storage import FsStorage
from app.db.object_storage_provider.json_storage import JsonStorage
from app.db.object_storage_provider.memory_storage import MemoryStorage
from app.db.queue_storage_provider.deque_storage import DequeStorage


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as clt:
        yield clt


@pytest.fixture(scope="module", params=["file_json", "fs", "memory"])
def object_storage(file_json, request):
    if request.param == "file_json":
        yield JsonStorage(file_json.name)
    elif request.param == "fs":
        yield FsStorage("/tmp/signal_bot")
        try:
            shutil.rmtree("/tmp/signal_bot")
        except FileNotFoundError:
            pass
    elif request.param == "memory":
        yield MemoryStorage()
    else:
        raise ValueError("Invalid object storage type")


@pytest.fixture(scope="function", params=["deque"])
def queue_storage(request):
    if request.param == "deque":
        return DequeStorage(5)
    return None


@pytest.fixture(scope="module", name="file_json")
def fixture_file_json():
    tmp_file = tempfile.NamedTemporaryFile(mode="w")
    tmp_file.write("{}")
    tmp_file.seek(0)
    yield tmp_file
    tmp_file.close()
