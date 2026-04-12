# Conditional statements as pytest-verified learning notes.
# Covers: if/elif/else, truthiness branching, ternary expressions, chained comparisons.


# ---------------------------------------------------------------------------
# 1. if / elif / else
# ---------------------------------------------------------------------------


def test_if_branch_taken_when_true() -> None:
    x = 10
    result = "yes" if x > 5 else "no"
    assert result == "yes"


def test_else_branch_taken_when_condition_false() -> None:
    x = 2
    if x > 5:  # noqa: SIM108 — teaching if/else form, not the ternary shorthand
        result = "big"
    else:
        result = "small"
    assert result == "small"


def test_elif_selects_first_matching_branch() -> None:
    def classify(n: int) -> str:
        if n < 0:
            return "negative"
        elif n == 0:  # noqa: RET505 — teaching elif chain explicitly
            return "zero"
        elif n < 10:
            return "small"
        else:
            return "large"

    assert classify(-1) == "negative"
    assert classify(0) == "zero"
    assert classify(5) == "small"
    assert classify(100) == "large"


def test_only_first_true_elif_runs() -> None:
    # Once a branch is taken, all later elif/else branches are skipped
    def label(n: int) -> str:
        if n > 0:
            return "positive"
        elif n > -10:  # noqa: RET505 — teaching elif chain explicitly
            return "small negative"
        else:
            return "large negative"

    assert label(5) == "positive"
    assert label(-3) == "small negative"
    assert label(-20) == "large negative"


# ---------------------------------------------------------------------------
# 2. Truthiness-based branching
# ---------------------------------------------------------------------------


def test_empty_list_is_falsy() -> None:
    items: list[int] = []
    if items:  # noqa: SIM108 — teaching if/else form explicitly
        result = "has items"
    else:
        result = "empty"
    assert result == "empty"


def test_non_empty_list_is_truthy() -> None:
    items = [0]  # a list containing a falsy value is still truthy
    if items:  # noqa: SIM108 — teaching if/else form explicitly
        result = "has items"
    else:
        result = "empty"
    assert result == "has items"


def test_none_is_falsy() -> None:
    value = None
    result = "got value" if value else "no value"
    assert result == "no value"


def test_zero_string_dict_are_falsy() -> None:
    for falsy in [0, 0.0, "", {}, [], ()]:
        assert not falsy


def test_truthy_defaults_pattern() -> None:
    # Common idiom: use `or` to supply a default when value is falsy
    name = ""
    display = name or "Anonymous"
    assert display == "Anonymous"

    name = "Alice"
    display = name or "Anonymous"
    assert display == "Alice"


# ---------------------------------------------------------------------------
# 3. Ternary (conditional) expression — value_if_true if condition else value_if_false
# ---------------------------------------------------------------------------


def test_ternary_returns_value_when_true() -> None:
    x = 7
    label = "odd" if x % 2 != 0 else "even"
    assert label == "odd"


def test_ternary_returns_value_when_false() -> None:
    x = 8
    label = "odd" if x % 2 != 0 else "even"
    assert label == "even"


def test_ternary_can_be_nested() -> None:
    # Nesting is possible but prefer elif chains for readability beyond two levels
    def sign(n: int) -> str:
        return "positive" if n > 0 else ("negative" if n < 0 else "zero")

    assert sign(5) == "positive"
    assert sign(-3) == "negative"
    assert sign(0) == "zero"


def test_ternary_evaluates_only_chosen_branch() -> None:
    # Only the selected branch expression is evaluated — no side effects from the other
    side_effects: list[str] = []

    def record(label: str) -> str:
        side_effects.append(label)
        return label

    result = record("true_branch") if True else record("false_branch")
    assert result == "true_branch"
    assert side_effects == ["true_branch"]


# ---------------------------------------------------------------------------
# 4. Chained comparisons
# ---------------------------------------------------------------------------


def test_chained_comparison_range_check() -> None:
    # 1 < x < 10 is evaluated as (1 < x) and (x < 10) — no repeated evaluation of x
    x = 5
    assert 1 < x < 10
    assert not (10 < x < 20)


def test_chained_comparison_with_equality() -> None:
    a = b = c = 5
    assert a == b == c


def test_chained_comparison_mixed_operators() -> None:
    assert 1 <= 2 < 3 <= 3  # noqa: PLR0133 — demonstrating mixed chained comparisons


def test_chained_comparison_middle_evaluated_once() -> None:
    # The middle expression in a chain is evaluated only once
    calls: list[int] = []

    def get(n: int) -> int:
        calls.append(n)
        return n

    result = 1 < get(5) < 10
    assert result is True
    assert len(calls) == 1  # get(5) called only once


# ---------------------------------------------------------------------------
# 5. bool() coercion and explicit truthiness tests
# ---------------------------------------------------------------------------


def test_bool_coercion_of_numbers() -> None:
    assert bool(0) is False
    assert bool(1) is True
    assert bool(-1) is True
    assert bool(0.0) is False


def test_bool_coercion_of_strings() -> None:
    assert bool("") is False
    assert bool(" ") is True  # whitespace-only string is truthy
    assert bool("0") is True  # the string "0" is truthy (non-empty)


def test_bool_coercion_of_collections() -> None:
    assert bool([]) is False
    assert bool([0]) is True
    assert bool({}) is False
    assert bool({"k": None}) is True


def test_custom_class_truthiness_via_bool_dunder() -> None:
    class Threshold:
        def __init__(self, value: int) -> None:
            self.value = value

        def __bool__(self) -> bool:
            return self.value > 0

    assert bool(Threshold(5)) is True
    assert bool(Threshold(0)) is False
    assert bool(Threshold(-1)) is False
