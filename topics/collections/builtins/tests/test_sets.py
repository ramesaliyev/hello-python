# Set examples as pytest-verified learning notes.

import pytest


def test_deduplication() -> None:
    some_set = {1, 2, 3, 4}
    assert some_set == {1, 2, 3, 4}


def test_empty_set() -> None:
    empty_set: set[int] = set()
    assert len(empty_set) == 0


def test_unhashable_element_raises() -> None:
    with pytest.raises(TypeError):
        {[1], 1}  # noqa: B018 — set literal is the point; list is unhashable


def test_tuple_element_is_valid() -> None:
    valid_set = {(1,), 1}
    assert (1,) in valid_set
    assert 1 in valid_set


def test_add() -> None:
    filled_set = {1, 2, 3, 4}
    filled_set.add(5)
    assert filled_set == {1, 2, 3, 4, 5}


def test_add_duplicate_has_no_effect() -> None:
    filled_set = {1, 2, 3, 4, 5}
    filled_set.add(5)
    assert filled_set == {1, 2, 3, 4, 5}


def test_intersection() -> None:
    assert {1, 2, 3, 4, 5} & {3, 4, 5, 6} == {3, 4, 5}


def test_union() -> None:
    assert {1, 2, 3, 4, 5} | {3, 4, 5, 6} == {1, 2, 3, 4, 5, 6}


def test_difference() -> None:
    assert {1, 2, 3, 4} - {2, 3, 5} == {1, 4}


def test_symmetric_difference() -> None:
    assert {1, 2, 3, 4} ^ {2, 3, 5} == {1, 4, 5}


def test_superset() -> None:
    assert ({1, 2} >= {1, 2, 3}) is False
    assert ({1, 2, 3} >= {1, 2}) is True


def test_subset() -> None:
    assert ({1, 2} <= {1, 2, 3}) is True
    assert ({1, 2, 3} <= {1, 2}) is False


def test_membership() -> None:
    filled_set = {1, 2, 3, 4, 5}
    assert 2 in filled_set
    assert 10 not in filled_set


def test_copy_is_equal_but_not_same() -> None:
    some_set = {1, 2, 3, 4, 5}
    filled_set = some_set.copy()
    assert filled_set == some_set
    assert filled_set is not some_set
