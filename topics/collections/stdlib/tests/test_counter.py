# collections.Counter: dict subclass for counting hashable objects.
#
# Counter behaves like defaultdict(int) for missing keys, but adds
# counting-specific operations that defaultdict lacks: most_common(),
# arithmetic, set-like intersection and union, subtract(), elements(),
# and total().
#
# Use defaultdict(int) when you need a general-purpose accumulator where the
# values happen to be ints. Use Counter when the values ARE counts and you
# want the full counting API.

from collections import Counter


def test_counter_from_iterable() -> None:
    # most common construction: pass an iterable, Counter tallies for you
    counts = Counter("banana")
    assert counts["a"] == 3
    assert counts["b"] == 1


def test_counter_missing_key_returns_zero() -> None:
    # like defaultdict(int) — no KeyError, just 0
    counts = Counter("banana")
    assert counts["z"] == 0


def test_counter_incremental_counting() -> None:
    # Counter() also works as an empty accumulator, just like defaultdict(int)
    counts: Counter[str] = Counter()
    for char in "banana":
        counts[char] += 1
    assert counts["a"] == 3
    # difference from defaultdict: reading a missing key does NOT insert it
    assert "z" not in counts
    assert counts["z"] == 0
    assert "z" not in counts  # still not inserted after the read


def test_counter_most_common() -> None:
    counts = Counter("abracadabra")
    top_two = counts.most_common(2)
    assert top_two[0] == ("a", 5)
    assert top_two[1] == ("b", 2)


def test_counter_total() -> None:
    # total() sums all counts — handy for computing frequencies
    counts = Counter("banana")
    assert counts.total() == 6


def test_counter_elements() -> None:
    # elements() expands each key by its count — the inverse of Counter()
    counts = Counter(a=3, b=1)
    assert sorted(counts.elements()) == ["a", "a", "a", "b"]


def test_counter_addition_combines_counts() -> None:
    # + adds counts; keys with zero or negative result are dropped
    c1 = Counter(a=3, b=1)
    c2 = Counter(a=1, b=2, c=5)
    combined = c1 + c2
    assert combined == Counter(a=4, b=3, c=5)


def test_counter_subtraction_removes_counts() -> None:
    # - subtracts counts; keys that hit zero or below are dropped from result
    c1 = Counter(a=5, b=3)
    c2 = Counter(a=2, b=4)
    result = c1 - c2
    assert result == Counter(a=3)  # b dropped: 3-4 = -1 ≤ 0


def test_counter_subtract_method_allows_negatives() -> None:
    # subtract() (the method, not -) keeps negative counts — useful for diffs
    c = Counter(a=5, b=3)
    c.subtract(Counter(a=2, b=4))
    assert c["a"] == 3
    assert c["b"] == -1  # negative — subtract() does not drop these


def test_counter_intersection_keeps_minimum_counts() -> None:
    # & gives the minimum count per key — "what both have"
    c1 = Counter(a=3, b=2, c=1)
    c2 = Counter(a=1, b=5)
    intersection = c1 & c2
    assert intersection == Counter(a=1, b=2)  # min per key; c absent from c2


def test_counter_union_keeps_maximum_counts() -> None:
    # | gives the maximum count per key — "the most of either"
    c1 = Counter(a=3, b=1)
    c2 = Counter(a=1, b=5, c=2)
    union = c1 | c2
    assert union == Counter(a=3, b=5, c=2)  # max per key
