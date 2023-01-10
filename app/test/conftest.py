import tempfile

import pytest
from fastapi.testclient import TestClient

from app.backend.api.main import app
from app.db.object_storage_provider.file_storage import FileStorage
from app.db.queue_storage_provider.deque_storage import DequeStorage


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as clt:
        yield clt


# fixture to create a FileStorage object
@pytest.fixture(scope="module", params=["file_json"])
def object_storage(file_json, request):
    if request.param == "file_json":
        return FileStorage(file_json.name)
    return None


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
