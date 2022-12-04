import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from signal_bot.backend.db.provider.file_storage import FileStorage
from signal_bot.backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# fixture to create a FileStorage object
@pytest.fixture(scope="module")
def file_storage(file_json):
    return FileStorage(file_json.name)


# fixture to create a temporary file json
@pytest.fixture(scope="module")
def file_json():
    tmp_file = tempfile.NamedTemporaryFile(mode="w")
    tmp_file.write("{}")
    tmp_file.seek(0)
    yield tmp_file
    tmp_file.close()
