import pytest

pytest.mark.parametrize("object_storage", ["file_json", "fs", "memory"], indirect=True)


def test_object_storage(object_storage):
    assert object_storage.get("test") is None
    assert object_storage.put("test", "test") is None
    assert object_storage.get("test") == "test"
    assert object_storage.put("un/dos/tres/test", "test") is None
    assert object_storage.get("un/dos/tres/test") == "test"
    assert object_storage.delete("test") is None
    assert object_storage.delete("un/dos/tres/test") is None
    assert object_storage.get("test") is None


pytest.mark.parametrize("object_storage", ["file_json", "fs", "memory"], indirect=True)


def test_object_storage_all(object_storage):
    assert object_storage.get_all() == {}
    assert object_storage.put_all({"test": "test"}) is None
    assert object_storage.get_all() == {"test": "test"}
