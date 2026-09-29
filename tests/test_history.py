from models.history import History


def test_starts_empty():
    assert History().get_all() == []


def test_add_stores_expression_and_result():
    history = History()
    history.add("5 + 3", "8")
    assert history.get_all() == [("5 + 3", "8")]


def test_entries_keep_insertion_order():
    history = History()
    history.add("1 + 1", "2")
    history.add("2 * 3", "6")
    assert history.get_all() == [("1 + 1", "2"), ("2 * 3", "6")]


def test_oldest_entry_is_dropped_when_cap_is_exceeded():
    history = History(max_entries=2)
    history.add("1 + 1", "2")
    history.add("2 + 2", "4")
    history.add("3 + 3", "6")
    assert history.get_all() == [("2 + 2", "4"), ("3 + 3", "6")]


def test_get_all_returns_a_copy():
    history = History()
    history.add("1 + 1", "2")
    history.get_all().clear()
    assert len(history.get_all()) == 1


def test_clear_removes_all_entries():
    history = History()
    history.add("1 + 1", "2")
    history.clear()
    assert history.get_all() == []
