# Python operators as pytest-verified learning notes.
# Covers: arithmetic, comparison, logical, identity, membership, augmented assignment.


# ---------------------------------------------------------------------------
# 1. Arithmetic operators
# ---------------------------------------------------------------------------


def test_addition() -> None:
    assert 2 + 3 == 5
    assert 1.5 + 2.5 == 4.0


def test_subtraction() -> None:
    assert 10 - 4 == 6
    assert -3 - 2 == -5


def test_multiplication() -> None:
    assert 3 * 4 == 12
    assert 2.5 * 2 == 5.0


def test_true_division_always_returns_float() -> None:
    # / always returns float, even when result is a whole number
    assert 10 / 2 == 5.0
    assert type(10 / 2) is float


def test_floor_division_truncates_toward_negative_infinity() -> None:
    # // rounds down, not toward zero — important for negative operands
    assert 7 // 2 == 3
    assert -7 // 2 == -4  # not -3: floor of -3.5 is -4


def test_modulo() -> None:
    assert 10 % 3 == 1
    assert -10 % 3 == 2  # sign follows the divisor in Python


def test_exponentiation() -> None:
    assert 2**10 == 1024
    assert 9**0.5 == 3.0


def test_string_repetition_with_multiplication() -> None:
    # * works on strings and lists as repetition
    assert "ab" * 3 == "ababab"
    assert [0] * 4 == [0, 0, 0, 0]


def test_string_concatenation_with_addition() -> None:
    assert "hello" + " " + "world" == "hello world"


# ---------------------------------------------------------------------------
# 2. Comparison operators
# ---------------------------------------------------------------------------


def test_equality() -> None:
    assert 1 == 1  # noqa: PLR0133 — demonstrating == on literals
    assert "a" == "a"  # noqa: PLR0133 — demonstrating == on literals
    assert 1 == 1.0  # noqa: PLR0133 — int and float compare by value


def test_inequality() -> None:
    assert 1 != 2  # type: ignore[comparison-overlap]  # noqa: PLR0133 — demonstrating != on literals
    assert "a" != "b"  # type: ignore[comparison-overlap]  # noqa: PLR0133 — demonstrating != on literals


def test_ordering() -> None:
    assert 3 < 5  # noqa: PLR0133 — demonstrating < on literals
    assert 5 > 3  # noqa: PLR0133 — demonstrating > on literals
    assert 3 <= 3  # noqa: PLR0133 — demonstrating <= on literals
    assert 3 >= 3  # noqa: PLR0133 — demonstrating >= on literals


def test_chained_comparisons() -> None:
    # Python allows chaining: 1 < x < 10 is evaluated as (1 < x) and (x < 10)
    x = 5
    assert 1 < x < 10
    assert 0 <= x <= 5
    assert not (6 < x < 10)


def test_comparison_returns_bool() -> None:
    result = 3 < 5  # noqa: PLR0133 — intentional: capturing comparison result for type check
    assert type(result) is bool
    assert result is True


# ---------------------------------------------------------------------------
# 3. Logical operators — and, or, not
# ---------------------------------------------------------------------------


def test_and_returns_first_falsy_or_last_value() -> None:
    # `and` short-circuits: returns the first falsy operand, or the last one
    assert (1 and 2) == 2  # and returns last truthy or first falsy
    assert (0 and 2) == 0  # noqa: SIM223 — 0 and 2: demonstrating and's return value
    assert ("" and "x") == ""  # noqa: SIM223 — "" and "x": demonstrating and's return value


def test_or_returns_first_truthy_or_last_value() -> None:
    # `or` short-circuits: returns the first truthy operand, or the last one
    assert (1 or 2) == 1  # noqa: SIM222 — or returns first truthy or last falsy
    assert (0 or 2) == 2  # noqa: SIM222 — 0 or 2: demonstrating or's return value
    assert (0 or "") == ""  # both falsy — returns last operand


def test_not_inverts_truthiness() -> None:
    assert False is not True  # noqa: PLR0133 — demonstrating not on literals
    assert True is not False  # noqa: PLR0133 — demonstrating not on literals
    assert 0 != True  # type: ignore[comparison-overlap]  # noqa: PLR0133 — demonstrating not on literals
    assert "" != True  # type: ignore[comparison-overlap]  # noqa: PLR0133 — demonstrating not on literals


def test_and_short_circuits() -> None:
    # The right side of `and` is never evaluated if the left is falsy
    side_effects: list[str] = []

    def record(label: str) -> bool:
        side_effects.append(label)
        return True

    False and record("right")  # noqa: SIM223
    assert side_effects == []  # record() was never called


def test_or_short_circuits() -> None:
    side_effects: list[str] = []

    def record(label: str) -> bool:
        side_effects.append(label)
        return True

    True or record("right")  # noqa: SIM222
    assert side_effects == []


# ---------------------------------------------------------------------------
# 4. Identity operators — is / is not
# ---------------------------------------------------------------------------


def test_is_checks_object_identity_not_value() -> None:
    a = [1, 2, 3]
    b = a  # same object
    c = [1, 2, 3]  # equal value, different object
    assert a is b
    assert a is not c
    assert a == c  # equal by value


def test_none_should_be_compared_with_is() -> None:
    # PEP 8 recommends `is None` / `is not None` rather than == None
    value = None
    assert value is None
    assert value is not True


def test_small_int_caching() -> None:
    # CPython caches small integers (-5 to 256) — they share identity
    a = 100
    b = 100
    assert a is b  # same cached object


def test_large_int_may_not_be_cached() -> None:
    # Integers outside the cache range are not guaranteed to share identity
    a = 1000
    b = 1000
    # Value equality always holds regardless of caching
    assert a == b


# ---------------------------------------------------------------------------
# 5. Membership operators — in / not in
# ---------------------------------------------------------------------------


def test_in_with_list() -> None:
    assert 3 in [1, 2, 3]
    assert 4 not in [1, 2, 3]


def test_in_with_string() -> None:
    assert "ell" in "hello"  # noqa: PLR0133 — demonstrating substring membership
    assert "xyz" not in "hello"  # noqa: PLR0133 — demonstrating substring membership


def test_in_with_dict_checks_keys() -> None:
    # `in` on a dict checks keys, not values; int can never be a str key
    d = {"a": 1, "b": 2}
    assert "a" in d
    assert 1 not in d  # type: ignore[comparison-overlap]


def test_in_with_set() -> None:
    assert 5 in {1, 3, 5}
    assert 2 not in {1, 3, 5}


def test_in_with_tuple() -> None:
    assert "x" in ("x", "y", "z")
    assert "w" not in ("x", "y", "z")


# ---------------------------------------------------------------------------
# 6. Augmented assignment operators
# ---------------------------------------------------------------------------


def test_augmented_add() -> None:
    x = 5
    x += 3
    assert x == 8


def test_augmented_subtract() -> None:
    x = 10
    x -= 4
    assert x == 6


def test_augmented_multiply() -> None:
    x = 3
    x *= 4
    assert x == 12


def test_augmented_divide() -> None:
    x: float = 10
    x /= 4
    assert x == 2.5


def test_augmented_floor_divide() -> None:
    x = 10
    x //= 3
    assert x == 3


def test_augmented_modulo() -> None:
    x = 10
    x %= 3
    assert x == 1


def test_augmented_power() -> None:
    x = 2
    x **= 8
    assert x == 256


def test_augmented_add_on_list_extends_in_place() -> None:
    # += on a list calls __iadd__ — extends in-place, unlike + which creates a new list
    original = [1, 2]
    alias = original
    original += [3, 4]
    assert original == [1, 2, 3, 4]
    assert alias is original  # same object — mutated in-place
