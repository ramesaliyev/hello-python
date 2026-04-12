# Dictionary key constraints as pytest-verified learning notes.
# Keys must be immutable (hashable) types: ints, floats, strings, tuples.
# Values can be of any type.


import pytest


def test_list_key_raises_type_error() -> None:
    # Lists are mutable and unhashable — cannot be used as dict keys
    with pytest.raises(TypeError, match="unhashable type"):
        _ = {[1, 2, 3]: "123"}


def test_tuple_key_is_valid() -> None:
    # Tuples are immutable and hashable — valid as dict keys
    d = {(1, 2, 3): [1, 2, 3]}
    assert d[(1, 2, 3)] == [1, 2, 3]


def test_tuple_key_accessible_without_parentheses() -> None:
    # d[1, 2, 3] is syntactic sugar for d[(1, 2, 3)] — the comma constructs the tuple
    d = {(1, 2, 3): "found"}
    assert d[1, 2, 3] == "found"

    # also works with variables
    a, b, c = 1, 2, 3
    assert d[a, b, c] == "found"


def test_int_key_is_valid() -> None:
    d = {1: "one"}
    assert d[1] == "one"


def test_float_key_is_valid() -> None:
    d = {3.14: "pi"}
    assert d[3.14] == "pi"


def test_string_key_is_valid() -> None:
    d = {"hello": "world"}
    assert d["hello"] == "world"


def test_setdefault_inserts_only_if_missing() -> None:
    # setdefault() sets the key only when it is absent — never overwrites
    d = {"one": 1}
    d.setdefault("five", 5)
    assert d["five"] == 5

    d.setdefault("five", 6)  # key already exists — value stays 5
    assert d["five"] == 5


def test_values_can_be_any_type() -> None:
    d = {
        "list": [1, 2, 3],
        "dict": {"nested": True},
        "none": None,
        "func": len,
    }
    assert d["list"] == [1, 2, 3]
    assert d["dict"] == {"nested": True}
    assert d["none"] is None
    assert d["func"] is len
