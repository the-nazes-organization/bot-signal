def test_object_storage(object_storage):
    assert object_storage.get("test") is None
    assert object_storage.put("test", "test") is None
    assert object_storage.get("test") == "test"
    assert object_storage.delete("test") is None
    assert object_storage.get("test") is None


def test_object_storage_all(object_storage):
    assert object_storage.get_all() == {}
    assert object_storage.put_all({"test": "test"}) is None
    assert object_storage.get_all() == {"test": "test"}
