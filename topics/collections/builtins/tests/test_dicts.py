# Dictionary mechanics: keys, values, mutation, views, merging.

import pytest

# ---------------------------------------------------------------------------
# 1. Key constraints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 2. Access and mutation
# ---------------------------------------------------------------------------


def test_get_returns_none_when_key_missing() -> None:
    d = {"a": 1}
    assert d.get("a") == 1
    assert d.get("b") is None


def test_get_returns_default_when_key_missing() -> None:
    d = {"a": 1}
    assert d.get("b", 0) == 0
    assert d.get("a", 0) == 1  # default ignored when key exists


def test_pop_removes_and_returns_value() -> None:
    d = {"a": 1, "b": 2}
    value = d.pop("a")
    assert value == 1
    assert "a" not in d


def test_pop_with_default_avoids_key_error() -> None:
    d = {"a": 1}
    assert d.pop("missing", None) is None


def test_pop_raises_when_key_missing_and_no_default() -> None:
    d = {"a": 1}
    with pytest.raises(KeyError):
        d.pop("missing")


def test_update_merges_another_dict() -> None:
    base = {"a": 1, "b": 2}
    base.update({"b": 99, "c": 3})
    assert base == {"a": 1, "b": 99, "c": 3}


def test_update_with_keyword_arguments() -> None:
    d = {"a": 1}
    d.update(b=2, c=3)
    assert d == {"a": 1, "b": 2, "c": 3}


# ---------------------------------------------------------------------------
# 3. Views — keys, values, items
# ---------------------------------------------------------------------------


def test_keys_returns_a_view_not_a_copy() -> None:
    d = {"a": 1, "b": 2}
    keys_view = d.keys()
    d["c"] = 3
    # view reflects the mutation
    assert "c" in keys_view


def test_values_view() -> None:
    d = {"a": 1, "b": 2}
    assert list(d.values()) == [1, 2]


def test_items_view_yields_key_value_pairs() -> None:
    d = {"a": 1, "b": 2}
    assert list(d.items()) == [("a", 1), ("b", 2)]


def test_items_unpacking_in_loop() -> None:
    d = {"x": 10, "y": 20}
    result = {k: v * 2 for k, v in d.items()}
    assert result == {"x": 20, "y": 40}


# ---------------------------------------------------------------------------
# 4. Merging — | and |= operators (Python 3.9+)
# ---------------------------------------------------------------------------
#
# Use | when you need a new merged dict and want to keep the originals intact.
# Use |= when you own the left-hand dict and an in-place update is fine.
#
# Both follow the same rule for conflicts: right-hand side wins.
#
# Prefer | / |= over {**a, **b} for plain dict merging (see section 5):
#   - Reads as an explicit merge operation, not a construction pattern.
#   - Only works with actual dicts (or dict subclasses that implement __or__).
#   - Slightly more efficient — no intermediate unpacking step.


def test_pipe_operator_merges_dicts_into_new_dict() -> None:
    a = {"x": 1, "y": 2}
    b = {"y": 99, "z": 3}
    merged = a | b
    assert merged == {"x": 1, "y": 99, "z": 3}
    assert a == {"x": 1, "y": 2}  # original unchanged


def test_pipe_equals_operator_updates_in_place() -> None:
    a = {"x": 1, "y": 2}
    a |= {"y": 99, "z": 3}
    assert a == {"x": 1, "y": 99, "z": 3}


def test_pipe_operator_chaining() -> None:
    # | chains naturally left-to-right; last writer wins for each key
    base = {"a": 1}
    patch1 = {"b": 2}
    patch2 = {"a": 99, "c": 3}
    result = base | patch1 | patch2
    assert result == {"a": 99, "b": 2, "c": 3}


# ---------------------------------------------------------------------------
# 5. Unpacking with **
# ---------------------------------------------------------------------------
#
# {**a, **b} predates the | operator (works back to Python 3.5) and is still
# the right tool in two situations:
#
#   1. Mixing dict merging with extra inline keys in a single expression:
#        config = {**defaults, "debug": True, **overrides}
#      | cannot do this — it only merges whole dicts.
#
#   2. Passing keyword arguments to a function from a dict:
#        func(**options)
#      | produces a new dict; ** passes the contents directly as kwargs.
#
# For straightforward dict-to-dict merges with no extra keys, prefer |.


def test_double_star_unpacking_in_dict_literal() -> None:
    defaults = {"color": "red", "size": 10}
    overrides = {"size": 20, "weight": 5}
    merged = {**defaults, **overrides}
    assert merged == {"color": "red", "size": 20, "weight": 5}


def test_double_star_mixing_inline_keys() -> None:
    # ** shines here: | cannot interleave inline keys between dicts
    defaults = {"host": "localhost", "port": 5432}
    result = {**defaults, "port": 9999, "debug": True}
    assert result == {"host": "localhost", "port": 9999, "debug": True}


def test_double_star_unpacking_passes_kwargs() -> None:
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    params = {"name": "Alice", "greeting": "Hi"}
    assert greet(**params) == "Hi, Alice!"


# ---------------------------------------------------------------------------
# 6. Insertion-ordered guarantee (Python 3.7+)
# ---------------------------------------------------------------------------


def test_dict_preserves_insertion_order() -> None:
    d = {}
    for key in ["c", "a", "b"]:
        d[key] = key.upper()
    assert list(d.keys()) == ["c", "a", "b"]
