# collections.defaultdict: auto-initialising missing keys with a factory function.

from collections import defaultdict


def test_defaultdict_auto_initialises_missing_keys() -> None:
    counts: defaultdict[str, int] = defaultdict(int)
    for char in "banana":
        counts[char] += 1
    assert counts["a"] == 3
    assert counts["b"] == 1
    assert counts["missing"] == 0  # auto-initialised to int() == 0


def test_defaultdict_with_list_factory() -> None:
    groups: defaultdict[str, list[int]] = defaultdict(list)
    for value, key in [(1, "odd"), (2, "even"), (3, "odd")]:
        groups[key].append(value)
    assert groups["odd"] == [1, 3]
    assert groups["even"] == [2]
