# Python's built-in scalar types and type system as pytest-verified learning notes.
# Covers: type(), isinstance(), truthiness, coercion, and the walrus operator.


import pytest

# ---------------------------------------------------------------------------
# 1. Scalar literals — int, float, str, bool, None, bytes
# ---------------------------------------------------------------------------


def test_int_literal() -> None:
    assert type(42) is int  # noqa: UP003 — teaching type() usage
    assert type(-7) is int
    assert type(0) is int  # noqa: UP003 — teaching type() usage


def test_float_literal() -> None:
    assert type(3.14) is float  # noqa: UP003 — teaching type() usage
    assert type(-0.5) is float


def test_str_literal() -> None:
    assert type("hello") is str  # noqa: UP003 — teaching type() usage
    assert type("") is str  # noqa: UP003 — teaching type() usage


def test_bool_literal() -> None:
    # bool is a subclass of int — True == 1 and False == 0
    assert type(True) is bool  # noqa: UP003, FBT003 — teaching type() with bool literals
    assert type(False) is bool  # noqa: UP003, FBT003 — teaching type() with bool literals
    assert True == 1  # noqa: PLR0133 — demonstrating bool/int equality
    assert False == 0  # noqa: PLR0133 — demonstrating bool/int equality


def test_none_literal() -> None:
    # type(None) returns NoneType — the only instance is None itself
    none_type = type(None)
    assert none_type.__name__ == "NoneType"
    assert None is None  # noqa: PLR0133 — demonstrating None identity


def test_bytes_literal() -> None:
    assert type(b"hello") is bytes  # noqa: UP003 — teaching type() usage
    assert b"abc"[0] == 97  # indexing bytes yields an int, not a character


# ---------------------------------------------------------------------------
# 2. type() introspection
# ---------------------------------------------------------------------------


def test_type_returns_exact_type() -> None:
    assert type(1) is int  # noqa: UP003 — teaching type() usage
    assert type(1.0) is float  # noqa: UP003 — teaching type() usage
    assert type("a") is str  # noqa: UP003 — teaching type() usage
    assert type(True) is bool  # noqa: UP003, FBT003 — teaching type() with bool literal


def test_type_of_bool_is_bool_not_int() -> None:
    # Even though bool inherits from int, type() returns the most-derived class
    assert type(True) is bool  # noqa: UP003, FBT003 — teaching type() with bool literal
    assert type(True) is not int  # noqa: UP003, FBT003 — demonstrating strictness of type()


def test_type_used_to_compare_exact_class() -> None:
    # type() equality check is strict — does not account for inheritance
    class Animal:
        pass

    class Dog(Animal):
        pass

    fido = Dog()
    assert type(fido) is Dog
    assert type(fido) is not Animal


# ---------------------------------------------------------------------------
# 3. isinstance() — type checking with inheritance support
# ---------------------------------------------------------------------------


def test_isinstance_exact_match() -> None:
    assert isinstance(42, int)
    assert isinstance("hi", str)
    assert isinstance(3.14, float)


def test_isinstance_respects_inheritance() -> None:
    # bool is a subclass of int, so isinstance(True, int) is True
    assert isinstance(True, int)  # noqa: FBT003 — True is intentional subject here
    assert isinstance(True, bool)  # noqa: FBT003 — True is intentional subject here


def test_isinstance_with_tuple_of_types() -> None:
    # Pass a tuple to check against multiple types at once
    assert isinstance(42, (int, str))
    assert isinstance("hi", (int, str))
    assert not isinstance(3.14, (int, str))


def test_type_equality_vs_isinstance_differ_for_subclasses() -> None:
    # type() is strict; isinstance() accepts subclasses
    assert type(True) is not int  # noqa: UP003, FBT003 — strict: bool ≠ int
    assert isinstance(True, int)  # noqa: FBT003 — lenient: bool IS-A int


# ---------------------------------------------------------------------------
# 4. Truthiness — every object has a boolean value
# ---------------------------------------------------------------------------


def test_zero_values_are_falsy() -> None:
    # Numeric zeros of every type are falsy
    assert not bool(0)
    assert not bool(0.0)
    assert not bool(0j)  # complex zero


def test_none_is_falsy() -> None:
    assert not bool(None)


def test_empty_collections_are_falsy() -> None:
    assert not bool([])
    assert not bool(())
    assert not bool({})
    assert not bool(set())
    assert not bool("")
    assert not bool(b"")


def test_non_empty_and_non_zero_are_truthy() -> None:
    assert bool(1)
    assert bool(-1)
    assert bool(0.1)
    assert bool("x")
    assert bool([0])  # list with a falsy element is still truthy
    assert bool((None,))


def test_bool_subclasses_int_arithmetic() -> None:
    # Since bool is a subclass of int, True and False participate in arithmetic
    assert True + True == 2  # demonstrating bool/int arithmetic
    assert True * 5 == 5  # demonstrating bool/int arithmetic
    assert False + 1 == 1  # demonstrating bool/int arithmetic


# ---------------------------------------------------------------------------
# 5. Type coercion — explicit conversion between types
# ---------------------------------------------------------------------------


def test_int_from_string() -> None:
    assert int("42") == 42
    assert int("-7") == -7


def test_int_from_float_truncates() -> None:
    # int() truncates toward zero — it does not round
    assert int(3.9) == 3
    assert int(-3.9) == -3


def test_int_with_base() -> None:
    assert int("ff", 16) == 255
    assert int("101", 2) == 5


def test_float_from_string() -> None:
    assert float("3.14") == 3.14
    assert float("1e2") == 100.0


def test_str_from_number() -> None:
    assert str(42) == "42"
    assert str(3.14) == "3.14"
    assert str(True) == "True"
    assert str(None) == "None"


def test_bool_from_value() -> None:
    assert bool(0) is False
    assert bool(1) is True
    assert bool("") is False
    assert bool("x") is True


def test_invalid_int_conversion_raises() -> None:
    with pytest.raises(ValueError):
        int("abc")


def test_invalid_float_conversion_raises() -> None:
    with pytest.raises(ValueError):
        float("not_a_number")


# ---------------------------------------------------------------------------
# 6. Walrus operator (:=) — assignment expression (Python 3.8+)
# ---------------------------------------------------------------------------


def test_walrus_assigns_and_returns_value() -> None:
    # := assigns the value AND evaluates to it in the same expression
    if (n := 10) > 5:
        result = n
    assert result == 10


def test_walrus_avoids_double_computation() -> None:
    # Classic use: compute once, check, then use — without calling twice
    data = [1, 2, 3, 4, 5]
    if (length := len(data)) > 3:
        summary = f"long list: {length} items"
    assert summary == "long list: 5 items"


def test_walrus_in_while_loop() -> None:
    # Walrus lets you write a sentinel-style loop cleanly
    items = [3, 1, 4, 1, 5]
    collected: list[int] = []
    index = 0
    while (val := items[index] if index < len(items) else None) is not None:
        collected.append(val)
        index += 1
    assert collected == [3, 1, 4, 1, 5]


def test_walrus_in_list_comprehension() -> None:
    # Capture an intermediate value without computing it twice
    numbers = [1, 2, 3, 4, 5]
    doubled_big = [y for x in numbers if (y := x * 2) > 6]
    assert doubled_big == [8, 10]
