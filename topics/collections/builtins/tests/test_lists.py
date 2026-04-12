# List mechanics as pytest-verified learning notes.
# Covers: creation, indexing, slicing, mutation, sorting, copying, and common patterns.


import copy

import pytest

# ---------------------------------------------------------------------------
# 1. Creation
# ---------------------------------------------------------------------------


def test_list_literal() -> None:
    lst = [1, 2, 3]
    assert len(lst) == 3


def test_list_from_iterable() -> None:
    assert list("abc") == ["a", "b", "c"]
    assert list(range(3)) == [0, 1, 2]


def test_list_can_hold_mixed_types() -> None:
    mixed = [1, "two", 3.0, None, True]
    assert len(mixed) == 5


def test_empty_list() -> None:
    empty: list[int] = []
    assert len(empty) == 0
    assert not empty  # empty list is falsy


# ---------------------------------------------------------------------------
# 2. Indexing — positive and negative
# ---------------------------------------------------------------------------


def test_positive_index() -> None:
    lst = [10, 20, 30]
    assert lst[0] == 10
    assert lst[2] == 30


def test_negative_index_counts_from_end() -> None:
    lst = [10, 20, 30]
    assert lst[-1] == 30
    assert lst[-3] == 10


def test_index_out_of_range_raises() -> None:
    with pytest.raises(IndexError):
        _ = [1, 2, 3][5]  # noqa: PLE0643 — intentional out-of-bounds to demonstrate IndexError


def test_nested_list_access_requires_chained_indexing() -> None:
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert matrix[1][2] == 6  # row first, then column


def test_tuple_index_raises_on_list() -> None:
    # matrix[1, 2] passes tuple (1, 2) as the index — lists don't support this
    # numpy arrays accept tuple indices for multi-dimensional access, plain lists don't
    matrix = [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(TypeError):
        _ = matrix[1, 2]  # type: ignore[call-overload]


# ---------------------------------------------------------------------------
# 3. Slicing — [start:stop:step]
# ---------------------------------------------------------------------------


def test_basic_slice() -> None:
    lst = [0, 1, 2, 3, 4]
    assert lst[1:4] == [1, 2, 3]


def test_slice_with_omitted_start() -> None:
    assert [0, 1, 2, 3][:2] == [0, 1]


def test_slice_with_omitted_stop() -> None:
    assert [0, 1, 2, 3][2:] == [2, 3]


def test_slice_returns_new_list() -> None:
    original = [1, 2, 3]
    sliced = original[:]
    assert sliced == original
    assert sliced is not original  # different object


def test_slice_with_step() -> None:
    lst = list(range(10))
    assert lst[::2] == [0, 2, 4, 6, 8]
    assert lst[1::2] == [1, 3, 5, 7, 9]


def test_negative_step_reverses() -> None:
    lst = [1, 2, 3, 4, 5]
    assert lst[::-1] == [5, 4, 3, 2, 1]


def test_slice_beyond_bounds_does_not_raise() -> None:
    # Unlike indexing, slicing silently clamps to the valid range
    assert [1, 2, 3][0:100] == [1, 2, 3]
    assert [1, 2, 3][10:20] == []


# ---------------------------------------------------------------------------
# 4. Mutation methods — append, extend, insert, pop, remove, clear
# ---------------------------------------------------------------------------


def test_append_adds_single_item() -> None:
    lst = [1, 2]
    lst.append(3)
    assert lst == [1, 2, 3]


def test_append_adds_list_as_single_element() -> None:
    # append([4, 5]) adds a list object, not its contents — use extend() for that
    lst: list[object] = [1, 2, 3]
    lst.append([4, 5])
    assert lst == [1, 2, 3, [4, 5]]
    assert len(lst) == 4


def test_extend_adds_all_elements() -> None:
    lst = [1, 2]
    lst.extend([3, 4])
    assert lst == [1, 2, 3, 4]


def test_extend_with_any_iterable() -> None:
    lst: list[int | str] = [1, 2]
    lst.extend("ab")
    assert lst == [1, 2, "a", "b"]


def test_insert_at_position() -> None:
    lst = [1, 3, 4]
    lst.insert(1, 2)  # insert 2 at index 1
    assert lst == [1, 2, 3, 4]


def test_insert_at_zero_prepends() -> None:
    lst = [2, 3]
    lst.insert(0, 1)
    assert lst == [1, 2, 3]


def test_pop_removes_and_returns_last() -> None:
    lst = [1, 2, 3]
    item = lst.pop()
    assert item == 3
    assert lst == [1, 2]


def test_pop_with_index() -> None:
    lst = [10, 20, 30]
    item = lst.pop(1)
    assert item == 20
    assert lst == [10, 30]


def test_pop_on_empty_raises() -> None:
    with pytest.raises(IndexError):
        [].pop()


def test_remove_deletes_first_occurrence() -> None:
    lst = [1, 2, 3, 2]
    lst.remove(2)
    assert lst == [1, 3, 2]  # only the first 2 is removed


def test_remove_missing_raises() -> None:
    with pytest.raises(ValueError):
        [1, 2, 3].remove(99)


def test_clear_empties_list() -> None:
    lst = [1, 2, 3]
    lst.clear()
    assert lst == []


# ---------------------------------------------------------------------------
# 5. Query methods — index, count
# ---------------------------------------------------------------------------


def test_index_returns_position_of_first_match() -> None:
    lst = [10, 20, 30, 20]
    assert lst.index(20) == 1  # first occurrence


def test_index_with_start_and_stop() -> None:
    lst = [10, 20, 30, 20]
    # search only within [2:] — skips the first 20
    assert lst.index(20, 2) == 3


def test_index_missing_raises() -> None:
    with pytest.raises(ValueError):
        [1, 2, 3].index(99)


def test_count_occurrences() -> None:
    lst = [1, 2, 2, 3, 2]
    assert lst.count(2) == 3
    assert lst.count(5) == 0


# ---------------------------------------------------------------------------
# 6. Sorting — sort() vs sorted()
# ---------------------------------------------------------------------------


def test_sort_modifies_in_place_and_returns_none() -> None:
    lst = [3, 1, 2]
    result = lst.sort()
    assert result is None  # sort() returns None — it is a mutation, not a new list
    assert lst == [1, 2, 3]


def test_sorted_returns_new_list_and_leaves_original_unchanged() -> None:
    original = [3, 1, 2]
    new = sorted(original)
    assert new == [1, 2, 3]
    assert original == [3, 1, 2]


def test_sort_reverse() -> None:
    lst = [1, 3, 2]
    lst.sort(reverse=True)
    assert lst == [3, 2, 1]


def test_sort_with_key() -> None:
    words = ["banana", "fig", "apple"]
    words.sort(key=len)
    assert words == ["fig", "apple", "banana"]


def test_reverse_method_reverses_in_place() -> None:
    lst = [1, 2, 3]
    lst.reverse()
    assert lst == [3, 2, 1]


# ---------------------------------------------------------------------------
# 7. List as stack (LIFO) and queue (FIFO)
# ---------------------------------------------------------------------------


def test_list_as_stack_lifo() -> None:
    # append() pushes; pop() pulls from the top — O(1) at the end
    stack: list[int] = []
    stack.append(1)
    stack.append(2)
    stack.append(3)
    assert stack.pop() == 3
    assert stack.pop() == 2


def test_list_as_queue_fifo_with_pop_zero() -> None:
    # pop(0) dequeues from the front — O(n); prefer collections.deque for real queues
    queue: list[int] = []
    queue.append(1)
    queue.append(2)
    queue.append(3)
    assert queue.pop(0) == 1
    assert queue.pop(0) == 2


# ---------------------------------------------------------------------------
# 8. Copying — reference vs shallow vs deep
# ---------------------------------------------------------------------------


def test_assignment_shares_same_object() -> None:
    a = [1, 2, 3]
    b = a  # b is an alias, not a copy
    b.append(4)
    assert a == [1, 2, 3, 4]  # a and b are the same list


def test_shallow_copy_creates_new_outer_list() -> None:
    original = [1, [2, 3]]
    shallow = original.copy()
    shallow.append(4)
    assert original == [1, [2, 3]]  # outer list unaffected

    shallow[1].append(99)  # type: ignore[attr-defined]
    assert original[1] == [2, 3, 99]  # inner list is still shared


def test_deep_copy_clones_nested_objects() -> None:
    original = [1, [2, 3]]
    deep = copy.deepcopy(original)
    deep[1].append(99)  # type: ignore[attr-defined]
    assert original[1] == [2, 3]  # inner list is independent


# ---------------------------------------------------------------------------
# 9. Concatenation and repetition
# ---------------------------------------------------------------------------


def test_concatenation_creates_new_list() -> None:
    a = [1, 2]
    b = [3, 4]
    c = a + b
    assert c == [1, 2, 3, 4]
    assert a == [1, 2]  # originals unchanged


def test_repetition() -> None:
    assert [0] * 5 == [0, 0, 0, 0, 0]
    assert [1, 2] * 3 == [1, 2, 1, 2, 1, 2]


def test_repetition_with_mutable_elements_shares_references() -> None:
    # All copies of a mutable inner object are the same object
    matrix = [[0] * 3] * 3
    matrix[0][0] = 9
    # Every row is the same list object — all rows are affected
    assert matrix[1][0] == 9
    assert matrix[2][0] == 9
