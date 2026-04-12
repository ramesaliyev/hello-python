# Commonly used Python built-in functions as pytest-verified learning notes.
# Covers: numeric, sequence, collection constructors, any/all, and formatting builtins.


import pytest

# ---------------------------------------------------------------------------
# 1. Numeric builtins — abs, round, pow, divmod, min, max, sum
# ---------------------------------------------------------------------------


def test_abs_positive_and_negative() -> None:
    assert abs(-5) == 5
    assert abs(5) == 5
    assert abs(-3.7) == 3.7


def test_round_half_to_even() -> None:
    # Python uses banker's rounding — ties round to the nearest even digit
    assert round(2.5) == 2  # rounds down to even
    assert round(3.5) == 4  # rounds up to even
    assert round(2.675, 2) != 2.68  # floating-point representation surprises


def test_round_with_ndigits() -> None:
    assert round(3.14159, 2) == 3.14
    # negative ndigits rounds at the tens/hundreds place
    assert round(12345, -2) == 12300


def test_pow_two_args() -> None:
    assert pow(2, 10) == 1024


def test_pow_three_args_modular_exponentiation() -> None:
    # pow(base, exp, mod) is more efficient than (base ** exp) % mod for large numbers
    assert pow(2, 10, 100) == 24  # (1024 % 100)


def test_divmod_returns_quotient_and_remainder() -> None:
    q, r = divmod(17, 5)
    assert q == 3
    assert r == 2


def test_min_and_max_on_sequence() -> None:
    data = [3, 1, 4, 1, 5, 9, 2]
    assert min(data) == 1
    assert max(data) == 9


def test_min_and_max_with_key() -> None:
    words = ["banana", "fig", "apple"]
    assert min(words, key=len) == "fig"
    assert max(words, key=len) == "banana"


def test_min_and_max_with_default() -> None:
    # default is returned instead of raising ValueError on an empty sequence
    assert min([], default=0) == 0
    assert max([], default=-1) == -1


def test_sum_with_start() -> None:
    # start value is added to the total — useful for initializing an accumulator
    assert sum([1, 2, 3]) == 6
    assert sum([1, 2, 3], 10) == 16


def test_sum_of_floats() -> None:
    assert sum([0.1, 0.2, 0.3]) == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# 2. Sequence builtins — len, sorted, reversed, enumerate, zip
# ---------------------------------------------------------------------------


def test_len_on_various_types() -> None:
    assert len([1, 2, 3]) == 3
    assert len("hello") == 5
    assert len({}) == 0
    assert len((1, 2)) == 2


def test_sorted_returns_new_list() -> None:
    original = [3, 1, 2]
    result = sorted(original)
    assert result == [1, 2, 3]
    assert original == [3, 1, 2]  # original is unchanged


def test_sorted_reverse() -> None:
    assert sorted([3, 1, 2], reverse=True) == [3, 2, 1]


def test_sorted_with_key() -> None:
    words = ["banana", "fig", "apple"]
    assert sorted(words, key=len) == ["fig", "apple", "banana"]


def test_reversed_returns_iterator() -> None:
    # reversed() returns an iterator, not a list — consume it with list()
    result = list(reversed([1, 2, 3]))
    assert result == [3, 2, 1]


def test_enumerate_yields_index_value_pairs() -> None:
    letters = ["a", "b", "c"]
    pairs = list(enumerate(letters))
    assert pairs == [(0, "a"), (1, "b"), (2, "c")]


def test_enumerate_with_start() -> None:
    letters = ["a", "b", "c"]
    pairs = list(enumerate(letters, start=1))
    assert pairs == [(1, "a"), (2, "b"), (3, "c")]


def test_zip_pairs_elements_from_multiple_iterables() -> None:
    names = ["Alice", "Bob"]
    scores = [95, 87]
    result = list(zip(names, scores, strict=True))
    assert result == [("Alice", 95), ("Bob", 87)]


def test_zip_stops_at_shortest() -> None:
    # zip() stops as soon as the shortest iterable is exhausted
    result = list(zip([1, 2, 3], ["a", "b"], strict=False))
    assert result == [(1, "a"), (2, "b")]


def test_zip_unzip_pattern() -> None:
    # zip(*pairs) transposes — unzips a list of tuples back into separate iterables
    pairs = [(1, "a"), (2, "b"), (3, "c")]
    numbers, letters = zip(*pairs, strict=True)
    assert list(numbers) == [1, 2, 3]
    assert list(letters) == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# 3. Collection constructors — list(), tuple(), dict(), set()
# ---------------------------------------------------------------------------


def test_list_from_iterable() -> None:
    assert list("abc") == ["a", "b", "c"]
    assert list(range(3)) == [0, 1, 2]
    assert list((1, 2, 3)) == [1, 2, 3]  # noqa: C410 — teaching list() from tuple


def test_tuple_from_iterable() -> None:
    assert tuple([1, 2, 3]) == (1, 2, 3)  # noqa: C409 — teaching tuple() from list
    assert tuple("hi") == ("h", "i")


def test_dict_from_key_value_pairs() -> None:
    assert dict([("a", 1), ("b", 2)]) == {"a": 1, "b": 2}  # noqa: C406 — teaching dict() from pairs


def test_dict_from_keyword_args() -> None:
    assert dict(x=1, y=2) == {"x": 1, "y": 2}  # noqa: C408 — teaching dict() keyword form


def test_set_from_iterable_deduplicates() -> None:
    result = set([1, 2, 2, 3, 3, 3])  # noqa: C405 — teaching set() from list
    assert result == {1, 2, 3}


# ---------------------------------------------------------------------------
# 4. range()
# ---------------------------------------------------------------------------


def test_range_one_arg() -> None:
    assert list(range(5)) == [0, 1, 2, 3, 4]


def test_range_two_args() -> None:
    assert list(range(2, 6)) == [2, 3, 4, 5]


def test_range_three_args_step() -> None:
    assert list(range(0, 10, 2)) == [0, 2, 4, 6, 8]


def test_range_negative_step() -> None:
    assert list(range(5, 0, -1)) == [5, 4, 3, 2, 1]


def test_range_is_reusable() -> None:
    # range is a sequence object, not a one-shot iterator
    r = range(3)
    assert list(r) == [0, 1, 2]
    assert list(r) == [0, 1, 2]  # still works


def test_range_supports_in_and_len() -> None:
    r = range(10)
    assert 5 in r
    assert len(r) == 10


# ---------------------------------------------------------------------------
# 5. any() and all()
# ---------------------------------------------------------------------------


def test_any_returns_true_if_at_least_one_truthy() -> None:
    assert any([False, False, True])
    assert not any([False, 0, "", None])


def test_all_returns_true_only_if_all_truthy() -> None:
    assert all([1, "x", [0]])
    assert not all([1, 0, "x"])


def test_any_short_circuits_on_first_truthy() -> None:
    # any() stops iterating once it finds a truthy value
    calls: list[int] = []

    def check(n: int) -> bool:
        calls.append(n)
        return n > 3

    result = any(check(n) for n in [1, 5, 2])
    assert result is True
    assert calls == [1, 5]  # stopped after finding 5 > 3


def test_all_short_circuits_on_first_falsy() -> None:
    calls: list[int] = []

    def check(n: int) -> bool:
        calls.append(n)
        return n < 10

    result = all(check(n) for n in [1, 20, 3])
    assert result is False
    assert calls == [1, 20]  # stopped after finding 20 is not < 10


def test_any_and_all_on_empty_sequence() -> None:
    # any([]) is False (no truthy element found); all([]) is True (vacuously true)
    assert not any([])
    assert all([])


# ---------------------------------------------------------------------------
# 6. repr(), str(), format()
# ---------------------------------------------------------------------------


def test_str_produces_human_readable_output() -> None:
    assert str(42) == "42"
    assert str([1, 2]) == "[1, 2]"


def test_repr_produces_unambiguous_representation() -> None:
    # repr() output should ideally be valid Python that recreates the object
    assert repr("hello") == "'hello'"
    assert repr([1, 2]) == "[1, 2]"


def test_str_vs_repr_differ_for_strings() -> None:
    # str() shows the content; repr() adds quotes so the type is unambiguous
    assert str("hi") == "hi"  # noqa: UP018 — teaching str() conversion explicitly
    assert repr("hi") == "'hi'"


def test_format_with_format_spec() -> None:
    assert format(3.14159, ".2f") == "3.14"
    assert format(255, "x") == "ff"  # hex
    assert format(42, "08b") == "00101010"  # zero-padded binary
