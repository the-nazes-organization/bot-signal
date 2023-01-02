def test_queue_storage(queue_storage):
    assert queue_storage.get() is None
    assert queue_storage.put("test") is None
    assert queue_storage.get() == "test"
    assert queue_storage.get() == "test"


def test_queue_storage_maxlen(queue_storage):
    assert queue_storage.get() is None
    for i in range(5):
        assert queue_storage.put(i) is None
    assert queue_storage.get_all() == [4, 3, 2, 1, 0]
    assert queue_storage.put(5) is None
    assert queue_storage.get_all() == [5, 4, 3, 2, 1]


def test_queue_storage_n_first(queue_storage):
    assert queue_storage.get() is None
    for i in range(5):
        assert queue_storage.put(i) is None
    assert queue_storage.get_all() == [4, 3, 2, 1, 0]
    assert queue_storage.get_n_last(3) == [4, 3, 2]
    assert queue_storage.get_all() == [4, 3, 2, 1, 0]
    assert queue_storage.get_n_last(10) == [4, 3, 2, 1, 0]
