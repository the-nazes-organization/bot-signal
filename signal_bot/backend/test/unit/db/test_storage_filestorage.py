def test_file_storage(file_storage):
    assert file_storage.get("test") is None
    assert file_storage.put("test", "test") is None
    assert file_storage.get("test") == "test"
    assert file_storage.delete("test") is None
    assert file_storage.get("test") is None


def test_file_storage_all(file_storage):
    assert file_storage.get_all() == {}
    assert file_storage.put_all({"test": "test"}) is None
    assert file_storage.get_all() == {"test": "test"}
