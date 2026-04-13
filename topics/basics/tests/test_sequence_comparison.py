# Lexicographic comparison of sequences: tuples, lists, and strings.

import pytest

# ---------------------------------------------------------------------------
# 1. Tuples are compared element by element (lexicographic order)
# ---------------------------------------------------------------------------


def test_tuple_comparison_first_differing_element_decides() -> None:
    # Elements are compared left to right; the first pair that differs
    # determines the result.
    assert (1, 2) < (1, 3)  # first elements equal, second decides
    assert (1, 2) > (1, 1)  # first elements equal, second decides
    assert (1, 9) < (2, 0)  # first element decides; second is never inspected


def test_tuple_equality_requires_all_elements_equal() -> None:
    assert (1, 2) == (1, 2)
    assert (1, 2) != (1, 3)


def test_tuple_comparison_supports_all_ordering_operators() -> None:
    low = (1, 0)
    high = (1, 5)

    assert low < high
    assert high > low
    assert low <= low  # noqa: PLR0124 — deliberately testing reflexivity
    assert high >= high  # noqa: PLR0124 — deliberately testing reflexivity


# ---------------------------------------------------------------------------
# 2. Comparison stops at the first differing element
# ---------------------------------------------------------------------------


def test_comparison_stops_at_first_difference() -> None:
    # If the result is decided early, later elements are never evaluated.
    # A custom class that raises if compared proves the early-exit behaviour.
    class NeverCompare:
        def __lt__(self, other: object) -> bool:
            raise AssertionError("should not be reached")

        def __gt__(self, other: object) -> bool:
            raise AssertionError("should not be reached")

    # (0, ...) vs (1, ...) — first element already decides;
    # NeverCompare is never touched.
    assert (0, NeverCompare()) < (1, NeverCompare())


# ---------------------------------------------------------------------------
# 3. Length matters when all shared elements are equal
# ---------------------------------------------------------------------------


def test_shorter_tuple_is_less_when_prefix_matches() -> None:
    # A tuple that is a prefix of another is considered "less than" it.
    assert (1,) < (1, 0)
    assert (1, 2) < (1, 2, 3)
    assert (1, 2) == (1, 2)


def test_empty_tuple_is_less_than_any_non_empty_tuple() -> None:
    assert () < (0,)
    assert () < (99,)


# ---------------------------------------------------------------------------
# 4. Lists compare the same way as tuples
# ---------------------------------------------------------------------------


def test_list_comparison_is_also_lexicographic() -> None:
    assert [1, 2] < [1, 3]  # same rules as tuples
    assert [1, 2] > [1, 1]
    assert [1, 2] == [1, 2]


def test_list_shorter_prefix_is_less() -> None:
    assert [1, 2] < [1, 2, 99]


# ---------------------------------------------------------------------------
# 5. Strings compare by Unicode code point
# ---------------------------------------------------------------------------


def test_string_comparison_is_lexicographic_by_code_point() -> None:
    assert "apple" < "banana"  # noqa: PLR0133 — 'a' (97) < 'b' (98)
    assert "abc" < "abd"  # noqa: PLR0133 — first two equal, 'c' (99) < 'd' (100)
    assert "abc" < "abcd"  # noqa: PLR0133 — prefix is less than extension


def test_string_uppercase_is_less_than_lowercase() -> None:
    # Uppercase letters have lower code points than lowercase:
    # ord('Z') = 90, ord('a') = 97.
    # This surprises developers who expect case-insensitive ordering.
    assert "Z" < "a"  # noqa: PLR0133 — ord('Z')=90 < ord('a')=97
    assert "Zoo" < "ant"  # noqa: PLR0133 — 'Z' < 'a' so the whole string is less


def test_case_insensitive_sort_requires_key() -> None:
    mixed = ["zebra", "Apple", "Mango"]

    # Default sort puts uppercase first because their code points are lower.
    assert sorted(mixed) == ["Apple", "Mango", "zebra"]

    # With str.lower as the key, comparison ignores case.
    assert sorted(mixed, key=str.lower) == ["Apple", "Mango", "zebra"]


# ---------------------------------------------------------------------------
# 6. Practical pattern — multi-field comparison via tuple packing
# ---------------------------------------------------------------------------


def test_tuple_packing_replaces_chained_field_comparisons() -> None:
    # Comparing (major, minor) as a tuple is the idiomatic way to impose
    # lexicographic order across multiple fields — the same pattern used in
    # functools.total_ordering implementations.
    #
    # Manual approach (verbose and error-prone):
    def version_lt_manual(a: tuple[int, int], b: tuple[int, int]) -> bool:
        major_a, minor_a = a
        major_b, minor_b = b
        if major_a != major_b:
            return major_a < major_b
        return minor_a < minor_b

    # Tuple packing approach (concise and correct):
    def version_lt_tuple(a: tuple[int, int], b: tuple[int, int]) -> bool:
        return a < b  # lexicographic comparison handles all cases automatically

    pairs = [((1, 0), (2, 0)), ((1, 5), (1, 9)), ((2, 0), (1, 99))]
    for a, b in pairs:
        assert version_lt_manual(a, b) == version_lt_tuple(a, b)


def test_sorting_records_by_multiple_fields_using_tuples() -> None:
    # Records as (name, score) — sort by score descending, then name ascending.
    records = [("alice", 90), ("bob", 95), ("carol", 90), ("dave", 85)]

    # Negate score so higher scores sort first; name sorts naturally.
    sorted_records = sorted(records, key=lambda r: (-r[1], r[0]))

    assert sorted_records == [("bob", 95), ("alice", 90), ("carol", 90), ("dave", 85)]


# ---------------------------------------------------------------------------
# 7. Pitfall — incompatible element types raise TypeError
# ---------------------------------------------------------------------------


def test_comparing_same_element_types_at_each_position_works() -> None:
    assert (1, "a") < (1, "b")  # str compared to str at position 1: fine
    assert (1, "a") < (2, "a")  # int compared to int at position 0: decided there


def test_incompatible_element_types_raise_type_error() -> None:
    with pytest.raises(TypeError):
        _ = (1, 2) < (1, "b")  # position 1: int vs str — Python cannot order these


def test_error_only_raised_when_incompatible_position_is_reached() -> None:
    # The first element already decides (0 < 1), so position 1
    # (int vs str) is never reached — no TypeError.
    assert (0, 2) < (1, "b")


# ---------------------------------------------------------------------------
# 8. Pitfall — cross-type sequence comparison raises TypeError
# ---------------------------------------------------------------------------


def test_list_and_tuple_cannot_be_ordered_with_less_than() -> None:
    # list and tuple do not share an ordering protocol.
    with pytest.raises(TypeError):
        _ = [1, 2] < (1, 3)  # type: ignore[operator]


def test_list_and_tuple_equality_returns_false_without_error() -> None:
    # == between list and tuple does not raise — it simply returns False.
    assert ([1, 2] == (1, 2)) is False  # type: ignore[comparison-overlap]  # intentional cross-type comparison — demonstrates it returns False, not TypeError
