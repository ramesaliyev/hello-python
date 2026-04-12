# Structural pattern matching (match/case, PEP 634, Python 3.10+)
# as pytest-verified learning notes.

from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------


@dataclass
class Point:
    x: float
    y: float


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


# ---------------------------------------------------------------------------
# 1. Literal patterns — match exact values
# ---------------------------------------------------------------------------


def test_literal_int() -> None:
    def classify(n: int) -> str:
        match n:
            case 0:
                return "zero"
            case 1:
                return "one"
            case _:
                return "other"

    assert classify(0) == "zero"
    assert classify(1) == "one"
    assert classify(99) == "other"


def test_literal_string() -> None:
    def greet(lang: str) -> str:
        match lang:
            case "en":
                return "hello"
            case "tr":
                return "merhaba"
            case _:
                return "unknown"

    assert greet("en") == "hello"
    assert greet("tr") == "merhaba"
    assert greet("de") == "unknown"


def test_literal_bool() -> None:
    # True and False are valid literal patterns;
    # they check identity, not just truthiness
    def describe(flag: bool) -> str:  # noqa: FBT001
        match flag:
            case True:
                return "yes"
            case False:
                return "no"

    assert describe(True) == "yes"  # noqa: FBT003
    assert describe(False) == "no"  # noqa: FBT003


def test_literal_none() -> None:
    def check(value: object) -> str:
        match value:
            case None:
                return "nothing"
            case _:
                return "something"

    assert check(None) == "nothing"
    assert check(0) == "something"
    assert check("") == "something"


def test_literal_no_match_returns_none() -> None:
    # When no case matches and there is no wildcard, match falls through silently
    def strict(n: int) -> str | None:
        match n:
            case 1:
                return "one"
            case 2:
                return "two"
        return None  # reached when nothing matched

    assert strict(1) == "one"
    assert strict(99) is None


# ---------------------------------------------------------------------------
# 2. Wildcard pattern — `_` catches anything without binding
# ---------------------------------------------------------------------------


def test_wildcard_catches_unmatched() -> None:
    def label(x: object) -> str:
        match x:
            case 42:
                return "the answer"
            case _:
                return "something else"

    assert label(42) == "the answer"
    assert label(0) == "something else"
    assert label("hi") == "something else"


def test_wildcard_does_not_bind() -> None:
    # `_` is NOT a capture — it is discarded and cannot be referenced afterwards
    result = "unset"
    match 99:
        case _:
            result = "matched"
    assert result == "matched"


# ---------------------------------------------------------------------------
# 3. Capture patterns — bind the matched value to a name
# ---------------------------------------------------------------------------


def test_capture_binds_value() -> None:
    # A bare name (not dotted) in a case is a capture — it always matches
    # and binds the subject to that name for the rest of the block
    match 7:
        case x:
            captured = x
    assert captured == 7


def test_capture_is_always_matched() -> None:
    # Captures work for any type — they are the "else" pattern with a name
    def first_match(v: object) -> object:
        match v:
            case 0:
                return "zero"
            case anything:  # matches everything not caught above
                return anything

    assert first_match(0) == "zero"
    assert first_match("hello") == "hello"
    assert first_match([1, 2]) == [1, 2]


# ---------------------------------------------------------------------------
# 4. OR patterns — `a | b` matches either alternative
# ---------------------------------------------------------------------------


def test_or_pattern_first_alternative() -> None:
    def weekend(day: str) -> bool:
        match day:
            case "Saturday" | "Sunday":
                return True
            case _:
                return False

    assert weekend("Saturday") is True
    assert weekend("Sunday") is True
    assert weekend("Monday") is False


def test_or_pattern_with_literals() -> None:
    def small_prime(n: int) -> bool:
        match n:
            case 2 | 3 | 5 | 7:
                return True
            case _:
                return False

    assert small_prime(3) is True
    assert small_prime(4) is False


def test_or_pattern_falls_through_to_next_case() -> None:
    # If OR pattern doesn't match, the next case is tried
    def classify(n: int) -> str:
        match n:
            case 1 | 2:
                return "low"
            case 3 | 4:
                return "mid"
            case _:
                return "high"

    assert classify(1) == "low"
    assert classify(4) == "mid"
    assert classify(10) == "high"


# ---------------------------------------------------------------------------
# 5. Guard clauses — add a condition with `if`
# ---------------------------------------------------------------------------


def test_guard_passes_when_condition_true() -> None:
    def sign(n: int) -> str:
        match n:
            case x if x > 0:
                return "positive"
            case x if x < 0:
                return "negative"
            case _:
                return "zero"

    assert sign(5) == "positive"
    assert sign(-3) == "negative"
    assert sign(0) == "zero"


def test_guard_falls_through_when_condition_false() -> None:
    # If the guard is False the case is skipped — even if the pattern matched
    def check(n: int) -> str:
        match n:
            case x if x % 2 == 0:
                return "even"
            case _:
                return "odd"

    assert check(4) == "even"
    assert check(7) == "odd"


def test_guard_with_sequence_pattern() -> None:
    def describe_pair(pair: list[int]) -> str:
        match pair:
            case [a, b] if a == b:
                return "equal"
            case [a, b] if a < b:
                return "ascending"
            case [_, _]:
                return "descending"
            case _:
                return "not a pair"

    assert describe_pair([3, 3]) == "equal"
    assert describe_pair([1, 5]) == "ascending"
    assert describe_pair([9, 2]) == "descending"
    assert describe_pair([1, 2, 3]) == "not a pair"


# ---------------------------------------------------------------------------
# 6. Sequence patterns — match lists / tuples by structure
# ---------------------------------------------------------------------------


def test_sequence_exact_length() -> None:
    def coords(seq: list[int]) -> str:
        match seq:
            case [x, y]:
                return f"2d:{x},{y}"
            case [x, y, z]:
                return f"3d:{x},{y},{z}"
            case _:
                return "unknown"

    assert coords([1, 2]) == "2d:1,2"
    assert coords([1, 2, 3]) == "3d:1,2,3"
    assert coords([1]) == "unknown"


def test_sequence_with_star_rest() -> None:
    # `*rest` captures the remaining elements as a list (may be empty)
    def head_tail(seq: list[int]) -> tuple[int, list[int]]:
        match seq:
            case [first, *rest]:
                return (first, rest)
            case _:
                return (-1, [])

    assert head_tail([10, 20, 30]) == (10, [20, 30])
    assert head_tail([42]) == (42, [])


def test_sequence_star_at_start() -> None:
    # `*` can appear at any position — not just at the end
    def last_two(seq: list[int]) -> tuple[int, int]:
        match seq:
            case [*_, a, b]:
                return (a, b)
            case _:
                return (0, 0)

    assert last_two([1, 2, 3, 4]) == (3, 4)
    assert last_two([7, 8]) == (7, 8)


def test_sequence_empty() -> None:
    def empty_check(seq: list[int]) -> str:
        match seq:
            case []:
                return "empty"
            case [_]:
                return "one element"
            case _:
                return "multiple"

    assert empty_check([]) == "empty"
    assert empty_check([1]) == "one element"
    assert empty_check([1, 2]) == "multiple"


def test_sequence_nested() -> None:
    # Patterns can be nested inside sequence slots
    def classify_matrix_row(row: list[list[int]]) -> str:
        match row:
            case [[0, 0], [0, 0]]:
                return "zero matrix row"
            case [[a, b], [c, d]]:
                return f"{a},{b},{c},{d}"
            case _:
                return "other"

    assert classify_matrix_row([[0, 0], [0, 0]]) == "zero matrix row"
    assert classify_matrix_row([[1, 2], [3, 4]]) == "1,2,3,4"


# ---------------------------------------------------------------------------
# 7. Mapping patterns — match dicts by key/value structure
# ---------------------------------------------------------------------------


def test_mapping_single_key() -> None:
    def get_action(event: dict[str, object]) -> str:
        match event:
            case {"type": "click"}:
                return "clicked"
            case {"type": "keypress"}:
                return "key pressed"
            case _:
                return "unknown event"

    assert get_action({"type": "click"}) == "clicked"
    assert get_action({"type": "keypress"}) == "key pressed"
    assert get_action({"type": "scroll"}) == "unknown event"


def test_mapping_multiple_keys() -> None:
    def parse_user(data: dict[str, object]) -> str:
        match data:
            case {"name": str(name), "age": int(age)}:
                return f"{name}:{age}"
            case _:
                return "invalid"

    assert parse_user({"name": "Alice", "age": 30}) == "Alice:30"
    assert parse_user({"name": "Bob"}) == "invalid"


def test_mapping_extra_keys_still_match() -> None:
    # Unlike sequence patterns, mapping patterns ignore extra keys by default
    def has_x(data: dict[str, object]) -> bool:
        match data:
            case {"x": _}:
                return True
            case _:
                return False

    assert has_x({"x": 1}) is True
    assert has_x({"x": 1, "y": 2, "z": 3}) is True  # extra keys are fine
    assert has_x({"y": 2}) is False


def test_mapping_with_double_star_rest() -> None:
    # `**rest` captures all keys that weren't explicitly matched
    def extract(data: dict[str, object]) -> tuple[object, dict[str, object]]:
        match data:
            case {"id": id_val, **rest}:
                return (id_val, rest)
            case _:
                return (None, {})

    assert extract({"id": 1, "name": "Alice", "role": "admin"}) == (
        1,
        {"name": "Alice", "role": "admin"},
    )
    assert extract({"id": 99}) == (99, {})


# ---------------------------------------------------------------------------
# 8. Class patterns — match instances by type and attributes
# ---------------------------------------------------------------------------


def test_class_pattern_type_only() -> None:
    # `case Point():` checks that the subject IS a Point (any attribute values)
    def is_point(obj: object) -> bool:
        match obj:
            case Point():
                return True
            case _:
                return False

    assert is_point(Point(1, 2)) is True
    assert is_point((1, 2)) is False


def test_class_pattern_attribute_match() -> None:
    def quadrant(p: Point) -> str:
        match p:
            case Point(x=0, y=0):
                return "origin"
            case Point(x=x, y=0):
                return f"x-axis at {x}"
            case Point(x=0, y=y):
                return f"y-axis at {y}"
            case Point(x=x, y=y) if x > 0 and y > 0:
                return "Q1"
            case Point(x=x, y=y) if x < 0 and y > 0:
                return "Q2"
            case _:
                return "other"

    assert quadrant(Point(0, 0)) == "origin"
    assert quadrant(Point(3, 0)) == "x-axis at 3"
    assert quadrant(Point(0, 5)) == "y-axis at 5"
    assert quadrant(Point(1, 2)) == "Q1"
    assert quadrant(Point(-1, 2)) == "Q2"


def test_class_pattern_positional_via_match_args() -> None:
    # Dataclasses expose __match_args__ = ('x', 'y'), enabling positional syntax
    def origin_check(p: Point) -> bool:
        match p:
            case Point(0, 0):  # positional: maps to x=0, y=0
                return True
            case _:
                return False

    assert origin_check(Point(0, 0)) is True
    assert origin_check(Point(1, 0)) is False


def test_class_pattern_builtin_int() -> None:
    # Built-in types like int/str support class patterns for type narrowing
    def describe(v: object) -> str:
        match v:
            case int(n) if n < 0:
                return "negative int"
            case int():
                return "non-negative int"
            case str():
                return "string"
            case _:
                return "other"

    assert describe(-5) == "negative int"
    assert describe(0) == "non-negative int"
    assert describe("hi") == "string"
    assert describe(3.14) == "other"


# ---------------------------------------------------------------------------
# 9. AS patterns — bind both the whole match and sub-pattern results
# ---------------------------------------------------------------------------


def test_as_pattern_binds_whole_value() -> None:
    # `case <pattern> as name:` gives access to the full matched subject
    def process(seq: list[int]) -> tuple[int, list[int]]:
        match seq:
            case [_, *_] as full_list:
                return (len(full_list), full_list)
            case _:
                return (0, [])

    length, lst = process([10, 20, 30])
    assert length == 3
    assert lst == [10, 20, 30]


def test_as_pattern_with_sequence_subpatterns() -> None:
    # AS pattern lets you destructure AND keep the original around
    def first_and_all(seq: list[int]) -> tuple[int, list[int]] | None:
        match seq:
            case [first, *_] as whole:
                return (first, whole)
            case _:
                return None

    result = first_and_all([5, 6, 7])
    assert result == (5, [5, 6, 7])


# ---------------------------------------------------------------------------
# 10. Value patterns — dotted names are looked up, not captured
# ---------------------------------------------------------------------------


def test_value_pattern_enum_match() -> None:
    # Bare names are captures; dotted names (Color.RED) are value lookups
    def color_name(c: Color) -> str:
        match c:
            case Color.RED:
                return "red"
            case Color.GREEN:
                return "green"
            case Color.BLUE:
                return "blue"

    assert color_name(Color.RED) == "red"
    assert color_name(Color.GREEN) == "green"
    assert color_name(Color.BLUE) == "blue"


def test_value_pattern_enum_no_match_falls_through() -> None:
    def is_warm(c: Color) -> bool:
        match c:
            case Color.RED:
                return True
            case _:
                return False

    assert is_warm(Color.RED) is True
    assert is_warm(Color.BLUE) is False


# ---------------------------------------------------------------------------
# 11. Nested / combined patterns — real-world-like compositions
# ---------------------------------------------------------------------------


def test_nested_mapping_with_sequence_value() -> None:
    # Mapping pattern whose value slot is itself a sequence pattern
    def route_event(event: dict[str, object]) -> str:
        match event:
            case {"type": "move", "coords": [x, y]}:
                return f"move to {x},{y}"
            case {"type": "resize", "size": [w, h]}:
                return f"resize to {w}x{h}"
            case _:
                return "unhandled"

    assert route_event({"type": "move", "coords": [10, 20]}) == "move to 10,20"
    assert route_event({"type": "resize", "size": [800, 600]}) == "resize to 800x600"
    assert route_event({"type": "click"}) == "unhandled"


def test_nested_class_inside_sequence() -> None:
    # Sequence slots can contain class patterns
    def describe_segment(points: list[Point]) -> str:
        match points:
            case [Point(0, 0), Point(x, y)]:
                return f"from origin to {x},{y}"
            case [Point(x1, y1), Point(x2, y2)]:
                return f"from {x1},{y1} to {x2},{y2}"
            case _:
                return "not a segment"

    assert describe_segment([Point(0, 0), Point(3, 4)]) == "from origin to 3,4"
    assert describe_segment([Point(1, 2), Point(3, 4)]) == "from 1,2 to 3,4"
    assert describe_segment([Point(0, 0)]) == "not a segment"


def test_combined_mapping_class_and_guard() -> None:
    # All pattern types at once: mapping + class + guard
    def validate_payload(payload: dict[str, object]) -> str:
        match payload:
            case {"origin": Point(x=x, y=y), "scale": float(s)} if s > 0:
                return f"valid: origin=({x},{y}) scale={s}"
            case {"origin": Point(), "scale": _}:
                return "invalid scale"
            case _:
                return "malformed"

    assert validate_payload({"origin": Point(1, 2), "scale": 1.5}) == (
        "valid: origin=(1,2) scale=1.5"
    )
    assert validate_payload({"origin": Point(0, 0), "scale": -1.0}) == "invalid scale"
    assert validate_payload({"origin": (0, 0), "scale": 1.0}) == "malformed"
