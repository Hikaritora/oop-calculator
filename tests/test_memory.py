from models.memory import Memory


def test_recall_starts_at_zero():
    memory = Memory()
    assert memory.recall() == 0


def test_add_sets_the_stored_value():
    memory = Memory()
    memory.add(5)
    assert memory.recall() == 5

    # add() overwrites the current value rather than accumulating -
    # that's how the controller implements M+ (it passes in the new total itself)
    memory.add(8)
    assert memory.recall() == 8


def test_subtract_decreases_the_stored_value():
    memory = Memory()
    memory.add(10)
    memory.subtract(4)
    assert memory.recall() == 6


def test_clear_resets_to_zero():
    memory = Memory()
    memory.add(42)
    memory.clear()
    assert memory.recall() == 0


def test_str_shows_the_current_value():
    memory = Memory()
    memory.add(7)
    assert "7" in str(memory)
