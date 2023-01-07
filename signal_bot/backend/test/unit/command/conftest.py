import pytest

import uuid
from datetime import datetime

from signal_bot.backend.schemas.data_formated import (
    DataFormated,
    User
)

@pytest.fixture(scope="function")
def bdata_formated():
    return DataFormated(
        id=str(uuid.uuid4()),
        sent_at=datetime.now(),
        user=User(
            nickname="tester",
            phone="+21309223",
            db_name="test"
        )
    )