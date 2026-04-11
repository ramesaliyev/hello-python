# Functional programming tools as pytest-verified learning notes.
# map, filter, reduce, operator module, partial application, and single dispatch.


from dataclasses import dataclass
from functools import partial, reduce, singledispatch
import operator

import pytest

# ---------------------------------------------------------------------------
# 1. map() — apply a function to every element
# ---------------------------------------------------------------------------


def test_map_applies_function_to_each_element() -> None:
    result = list(map(lambda x: x * 2, [1, 2, 3]))  # noqa: C417 — map+lambda form is the subject of this test
    assert result == [2, 4, 6]


def test_map_returns_an_iterator_not_a_list() -> None:
    # map() is lazy — it produces values on demand
    mapped = map(str, [1, 2, 3])
    assert not isinstance(mapped, list)
    assert list(mapped) == ["1", "2", "3"]


def test_map_with_named_function() -> None:
    assert list(map(abs, [-1, -2, 3])) == [1, 2, 3]


def test_map_with_multiple_iterables() -> None:
    # When multiple iterables are given, function receives one element from each
    result = list(map(operator.add, [1, 2, 3], [10, 20, 30], strict=True))
    assert result == [11, 22, 33]


def test_map_stops_at_shortest_iterable() -> None:
    # strict=False (default) — silently stops when the shorter iterable is exhausted
    result = list(map(operator.add, [1, 2, 3], [10, 20], strict=False))
    assert result == [11, 22]  # stops when the shorter one runs out


# ---------------------------------------------------------------------------
# 2. filter() — keep elements where predicate is True
# ---------------------------------------------------------------------------


def test_filter_keeps_truthy_elements() -> None:
    result = list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
    assert result == [2, 4]


def test_filter_returns_an_iterator() -> None:
    filtered = filter(lambda x: x > 0, [-1, 0, 1, 2])
    assert not isinstance(filtered, list)
    assert list(filtered) == [1, 2]


def test_filter_none_removes_falsy_values() -> None:
    # Passing None as the function keeps only truthy elements
    result = list(filter(None, [0, 1, "", "a", None, False, True]))
    assert result == [1, "a", True]


# ---------------------------------------------------------------------------
# 3. Iterator exhaustion — map/filter can only be consumed once
# ---------------------------------------------------------------------------


def test_map_iterator_exhausts_after_one_pass() -> None:
    mapped = map(str, [1, 2, 3])
    first = list(mapped)
    second = list(mapped)  # already drained
    assert first == ["1", "2", "3"]
    assert second == []  # empty — the iterator is exhausted


def test_filter_iterator_exhausts_after_one_pass() -> None:
    filtered = filter(None, [1, 2, 3])
    list(filtered)
    assert list(filtered) == []


# ---------------------------------------------------------------------------
# 4. functools.reduce() — cumulative application
# ---------------------------------------------------------------------------


def test_reduce_sums_a_list() -> None:
    assert reduce(operator.add, [1, 2, 3, 4]) == 10


def test_reduce_with_initial_value() -> None:
    # The initial value is the first accumulator; allows reducing empty sequences
    assert reduce(operator.add, [], 0) == 0
    assert reduce(operator.add, [1, 2, 3], 100) == 106


def test_reduce_builds_string_step_by_step() -> None:
    # reduce(f, [a, b, c]) → f(f(a, b), c)
    result = reduce(lambda acc, x: acc + x, ["a", "b", "c"])
    assert result == "abc"


def test_reduce_without_initial_on_single_element_returns_element() -> None:
    assert reduce(operator.mul, [7]) == 7


# ---------------------------------------------------------------------------
# 5. operator module — replace common lambdas with named functions
# ---------------------------------------------------------------------------


def test_operator_add_replaces_lambda() -> None:
    assert operator.add(3, 4) == 7
    assert list(map(operator.add, [1, 2], [3, 4], strict=True)) == [4, 6]


def test_itemgetter_retrieves_by_index_or_key() -> None:
    get_second = operator.itemgetter(1)
    assert get_second([10, 20, 30]) == 20

    get_name = operator.itemgetter("name")
    assert get_name({"name": "alice", "age": 30}) == "alice"


def test_itemgetter_as_sort_key() -> None:
    pairs = [(3, "c"), (1, "a"), (2, "b")]
    assert sorted(pairs, key=operator.itemgetter(0)) == [(1, "a"), (2, "b"), (3, "c")]


def test_attrgetter_retrieves_object_attribute() -> None:
    @dataclass
    class Point:
        x: int
        y: int

    points = [Point(3, 1), Point(1, 4), Point(2, 2)]
    sorted_by_x = sorted(points, key=operator.attrgetter("x"))
    assert [p.x for p in sorted_by_x] == [1, 2, 3]


def test_methodcaller_calls_named_method() -> None:
    upper = operator.methodcaller("upper")
    assert upper("hello") == "HELLO"

    words = ["BANANA", "APPLE", "CHERRY"]
    assert sorted(words, key=operator.methodcaller("lower")) == [
        "apple",
        "banana",
        "cherry",
    ]


def test_methodcaller_with_arguments() -> None:
    strip_dots = operator.methodcaller("strip", ".")
    assert strip_dots("...hello...") == "hello"


# ---------------------------------------------------------------------------
# 6. Lazy chaining — compose map/filter without materialising intermediates
# ---------------------------------------------------------------------------


def test_chained_map_and_filter_are_lazy() -> None:
    # Neither map nor filter runs until the chain is consumed
    log: list[int] = []

    def double_and_log(x: int) -> int:
        log.append(x)
        return x * 2

    pipeline = filter(lambda x: x > 4, map(double_and_log, range(5)))
    assert log == []  # nothing has run yet

    result = list(pipeline)
    assert result == [6, 8]  # 3*2=6 and 4*2=8 pass the filter
    assert len(log) == 5  # all elements were mapped (filter pulls from map)


def test_filter_is_not_subscriptable() -> None:
    # filter returns an iterator, not a sequence — index access is not supported
    pipeline = filter(lambda x: x > 4, (x * 2 for x in range(5)))
    with pytest.raises(TypeError):
        _ = pipeline[0]  # type: ignore[index]


def test_next_on_filter_only_computes_until_first_match() -> None:
    # next() pulls exactly as many elements as needed to satisfy the predicate
    log: list[int] = []

    def double_and_log(x: int) -> int:
        log.append(x)
        return x * 2

    # pipeline: range(5) → double_and_log → filter(> 4)
    # First passing value is 3*2=6; inputs 0,1,2,3 must be consumed to reach it
    pipeline = filter(lambda x: x > 4, map(double_and_log, range(5)))
    first = next(pipeline)

    assert first == 6
    assert log == [0, 1, 2, 3]  # only 4 elements processed, not all 5


# ---------------------------------------------------------------------------
# 7. functools.partial — partial application
# ---------------------------------------------------------------------------


def test_partial_fixes_keyword_argument() -> None:
    def power(base: int, exp: int) -> int:
        return base**exp  # type: ignore[no-any-return]

    square = partial(power, exp=2)
    cube = partial(power, exp=3)
    assert square(4) == 16
    assert cube(3) == 27


def test_partial_fixes_leading_positional_args() -> None:
    double = partial(operator.mul, 2)
    assert double(5) == 10
    assert double(7) == 14


def test_partial_creates_new_callable_does_not_mutate_original() -> None:
    def add(x: int, y: int) -> int:
        return x + y

    add10 = partial(add, 10)
    assert add10(5) == 15
    assert add(3, 4) == 7  # original function unchanged


def test_partial_can_be_further_partially_applied() -> None:
    def f(a: int, b: int, c: int) -> int:
        return a + b + c

    f1 = partial(f, 1)
    f12 = partial(f1, 2)
    assert f12(3) == 6


# ---------------------------------------------------------------------------
# 8. functools.singledispatch — dispatch on type of the first argument
# ---------------------------------------------------------------------------


def test_singledispatch_routes_to_type_specific_implementation() -> None:
    @singledispatch
    def describe(value: object) -> str:
        return f"unknown: {value!r}"

    @describe.register(int)
    def _(value: int) -> str:
        return f"integer: {value}"

    @describe.register(str)
    def _(value: str) -> str:
        return f"string: {value!r}"

    assert describe(42) == "integer: 42"
    assert describe("hi") == "string: 'hi'"
    assert describe(3.14) == "unknown: 3.14"  # falls back to base implementation


def test_singledispatch_dispatch_lookup() -> None:
    @singledispatch
    def process(x: object) -> str:  # noqa: ARG001
        return "base"

    @process.register(list)
    def _(x: list) -> str:  # type: ignore[type-arg]  # noqa: ARG001
        return "list"

    assert process([1, 2]) == "list"
    assert process.dispatch(list) is not process.dispatch(object)


def test_singledispatch_uses_mro_for_subclasses() -> None:
    @singledispatch
    def kind(x: object) -> str:  # noqa: ARG001
        return "object"

    @kind.register(bool)
    def _(x: bool) -> str:  # noqa: ARG001, FBT001
        return "bool"

    @kind.register(int)
    def _(x: int) -> str:  # noqa: ARG001
        return "int"

    # bool is a subclass of int — the most specific registered type wins
    assert kind(True) == "bool"  # noqa: FBT003
    assert kind(1) == "int"
    assert kind("x") == "object"
