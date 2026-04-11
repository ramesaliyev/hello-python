# Iterable and iterator protocol as pytest-verified learning notes.
# An iterable is any object with __iter__; an iterator additionally has __next__.


import pytest

# ---------------------------------------------------------------------------
# 1. Iterables — objects you can loop over but cannot index by position
# ---------------------------------------------------------------------------


def test_dict_keys_is_iterable() -> None:
    # dict.keys() returns a dict_keys view, which implements the Iterable protocol
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterable = filled_dict.keys()
    assert list(our_iterable) == ["one", "two", "three"]


def test_dict_keys_does_not_support_indexing() -> None:
    # dict_keys is not a sequence — integer indexing raises TypeError
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterable = filled_dict.keys()
    with pytest.raises(TypeError):
        _ = our_iterable[1]  # type: ignore[index]


def test_iterable_survives_multiple_for_loops() -> None:
    # Iterables are reusable — each for loop creates a fresh iterator internally
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterable = filled_dict.keys()
    first_pass = list(our_iterable)
    second_pass = list(our_iterable)
    assert first_pass == second_pass


# ---------------------------------------------------------------------------
# 2. Creating an iterator — iter() and next()
# ---------------------------------------------------------------------------


def test_iter_creates_iterator_from_iterable() -> None:
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterator = iter(filled_dict.keys())
    assert next(our_iterator) == "one"
    assert next(our_iterator) == "two"
    assert next(our_iterator) == "three"


def test_iterator_raises_stopiteration_when_exhausted() -> None:
    # After all elements are consumed the iterator raises StopIteration
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterator = iter(filled_dict.keys())
    next(our_iterator)
    next(our_iterator)
    next(our_iterator)
    with pytest.raises(StopIteration):
        next(our_iterator)


def test_next_with_default_avoids_stopiteration() -> None:
    # next() accepts an optional default value returned instead of raising
    our_iterator = iter([1])
    assert next(our_iterator, None) == 1
    assert next(our_iterator, None) is None  # exhausted — returns default


# ---------------------------------------------------------------------------
# 3. Iterator protocol — iterators are also iterables
# ---------------------------------------------------------------------------


def test_iterator_is_its_own_iterable() -> None:
    # iter() called on an iterator returns the same object
    our_iterator = iter(["a", "b"])
    assert iter(our_iterator) is our_iterator


def test_for_loop_uses_iterator_protocol_implicitly() -> None:
    # `for` calls iter() then repeatedly calls next() under the hood
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterator = iter(filled_dict.keys())
    collected = []
    for item in our_iterator:
        collected.append(item)  # noqa: PERF402 -- we on purpose want to iterate it
    assert collected == ["one", "two", "three"]


def test_iterator_exhausted_after_for_loop() -> None:
    # After a for loop drains an iterator it is permanently exhausted
    our_iterator = iter(["one", "two", "three"])
    for _ in our_iterator:
        pass
    assert list(our_iterator) == []


# ---------------------------------------------------------------------------
# 4. Consuming iterables/iterators — list(), tuple(), sum(), etc.
# ---------------------------------------------------------------------------


def test_list_consumes_iterable_fully() -> None:
    filled_dict = {"one": 1, "two": 2, "three": 3}
    our_iterable = filled_dict.keys()
    assert list(our_iterable) == ["one", "two", "three"]


def test_list_on_exhausted_iterator_returns_empty() -> None:
    # Calling list() on an exhausted iterator gives [] — state is not reset
    our_iterator = iter(["one", "two", "three"])
    list(our_iterator)  # first consumption drains the iterator
    assert list(our_iterator) == []


def test_iterable_reusable_but_iterator_is_not() -> None:
    # The same iterable can produce fresh iterators; exhausted iterators cannot
    our_iterable = {"one": 1, "two": 2}.keys()
    first_iter = iter(our_iterable)
    list(first_iter)  # drain it

    second_iter = iter(our_iterable)  # new iterator from the same iterable
    assert list(second_iter) == ["one", "two"]


def test_partial_consumption_preserves_remaining_state() -> None:
    # next() calls advance the cursor — list() picks up from where next() left off
    our_iterator = iter(["one", "two", "three"])
    next(our_iterator)  # consume "one"
    assert list(our_iterator) == ["two", "three"]


# ---------------------------------------------------------------------------
# 5. Edge cases and must-know behaviors
# ---------------------------------------------------------------------------


def test_iter_on_non_iterable_raises_type_error() -> None:
    # Passing a plain integer (no __iter__) to iter() raises TypeError
    with pytest.raises(TypeError):
        iter(42)  # type: ignore[call-overload]


def test_list_is_both_iterable_and_supports_indexing() -> None:
    # Lists implement __iter__ AND __getitem__, so they are sequences too
    lst = [10, 20, 30]
    our_iterator = iter(lst)
    assert next(our_iterator) == 10
    assert lst[2] == 30  # indexing still works on the original list


def test_string_is_iterable_character_by_character() -> None:
    # Strings implement the iterable protocol — each element is a single character
    chars = list(iter("abc"))
    assert chars == ["a", "b", "c"]


def test_range_is_iterable_and_reusable() -> None:
    # range() is an iterable (not an iterator) — can be looped multiple times
    r = range(3)
    assert list(r) == [0, 1, 2]
    assert list(r) == [0, 1, 2]  # still intact


def test_range_iterator_exhausts() -> None:
    r = range(2)
    it = iter(r)
    assert next(it) == 0
    assert next(it) == 1
    with pytest.raises(StopIteration):
        next(it)
