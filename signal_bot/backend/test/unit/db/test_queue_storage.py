
def test_queue_storage(queue_storage):
    assert queue_storage.get() is None
    assert queue_storage.put("test") is None
    assert queue_storage.get() == "test"
    assert queue_storage.get() == "test"

def test_queue_storage_maxlen(queue_storage):
    assert queue_storage.get() is None
    for i in range(5):
        assert queue_storage.put(i) is None
    assert queue_storage.get_all() == [0, 1, 2, 3, 4]
    assert queue_storage.put(5) is None
    assert queue_storage.get_all() == [1, 2, 3, 4, 5]

def test_queue_storage_n_first(queue_storage):
    assert queue_storage.get() is None
    for i in range(5):
        assert queue_storage.put(i) is None
    assert queue_storage.get_all() == [0, 1, 2, 3, 4]
    assert queue_storage.get_n_first(3) == [0, 1, 2]
    assert queue_storage.get_all() == [0, 1, 2, 3, 4]
    assert queue_storage.get_n_first(10) == [0, 1, 2, 3, 4]
