# yield from: delegation to sub-generators, transparent value/exception forwarding,
# and practical refactoring patterns.

from collections.abc import Generator

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TreeNode:
    def __init__(self, value: int, children: list[TreeNode] | None = None) -> None:
        self.value = value
        self.children = children or []


# ---------------------------------------------------------------------------
# 1. Delegation basics
# ---------------------------------------------------------------------------


def test_yield_from_delegates_to_sub_iterable() -> None:
    def gen() -> Generator[int]:
        yield from [1, 2, 3]

    assert list(gen()) == [1, 2, 3]


def test_yield_from_delegates_to_sub_generator() -> None:
    def inner() -> Generator[int]:
        yield 1
        yield 2

    def outer() -> Generator[int]:
        yield 0
        yield from inner()
        yield 3

    assert list(outer()) == [0, 1, 2, 3]


def test_yield_from_chains_multiple_iterables() -> None:
    def chained() -> Generator[int]:
        yield from range(3)
        yield from range(10, 13)
        yield from [20, 21]

    assert list(chained()) == [0, 1, 2, 10, 11, 12, 20, 21]


# ---------------------------------------------------------------------------
# 2. Value and exception forwarding
# ---------------------------------------------------------------------------


def test_yield_from_captures_sub_generator_return_value() -> None:
    def sub() -> Generator[int, None, str]:
        yield 1
        yield 2
        return "sub done"

    def outer() -> Generator[int]:
        result = yield from sub()
        # result receives the value from sub's return statement
        assert result == "sub done"
        yield 99

    assert list(outer()) == [1, 2, 99]


def test_yield_from_passes_send_values_to_sub_generator() -> None:
    received: list[int] = []

    def sub() -> Generator[int, int]:
        first = yield 0
        received.append(first)
        second = yield 1
        received.append(second)

    def outer() -> Generator[int, int]:
        yield from sub()

    gen = outer()
    next(gen)  # advance to first yield in sub (yields 0)
    gen.send(10)  # forwarded to sub; sub advances to yield 1 (yields 1)
    with pytest.raises(StopIteration):
        gen.send(20)  # sub gets 20, then ends → StopIteration

    assert received == [10, 20]


def test_yield_from_propagates_throw_to_sub_generator() -> None:
    caught: list[str] = []

    def sub() -> Generator[int]:
        try:
            yield 1
        except ValueError as exc:
            caught.append(str(exc))
            yield 2

    def outer() -> Generator[int]:
        yield from sub()

    gen = outer()
    next(gen)
    gen.throw(ValueError("injected"))

    assert caught == ["injected"]


def test_yield_from_with_plain_iterable_only_supports_none_sends() -> None:
    def outer() -> Generator[int, int | None]:
        # A plain list has no send() channel
        yield from [10, 20, 30]

    gen = outer()
    first = next(gen)
    second = gen.send(None)  # None is fine — treated as next() internally

    # Sending a non-None value raises AttributeError because list_iterator has no send()
    with pytest.raises(AttributeError):
        gen.send(999)

    assert first == 10
    assert second == 20


# ---------------------------------------------------------------------------
# 3. Practical patterns
# ---------------------------------------------------------------------------


def test_yield_from_simplifies_recursive_generator() -> None:
    def traverse(node: TreeNode) -> Generator[int]:
        yield node.value
        for child in node.children:
            yield from traverse(child)  # clean recursion — no manual for/yield loop

    tree = TreeNode(
        1,
        [
            TreeNode(2, [TreeNode(4), TreeNode(5)]),
            TreeNode(3),
        ],
    )

    assert list(traverse(tree)) == [1, 2, 4, 5, 3]


def test_yield_from_flattens_nested_iterables_one_level() -> None:
    def flatten_one_level(nested: list[list[int]]) -> Generator[int]:
        for sublist in nested:
            yield from sublist

    data = [[1, 2], [3, 4], [5]]
    assert list(flatten_one_level(data)) == [1, 2, 3, 4, 5]


def test_yield_from_for_composing_generator_pipelines() -> None:
    def evens(n: int) -> Generator[int]:
        yield from (x for x in range(n) if x % 2 == 0)

    def odds(n: int) -> Generator[int]:
        yield from (x for x in range(n) if x % 2 != 0)

    def combined(n: int) -> Generator[int]:
        yield from evens(n)
        yield from odds(n)

    assert list(combined(6)) == [0, 2, 4, 1, 3, 5]


# ---------------------------------------------------------------------------
# 4. Pitfalls
# ---------------------------------------------------------------------------


def test_yield_from_only_flattens_one_level() -> None:
    def flatten_one_level(nested: list[object]) -> Generator[object]:
        for item in nested:
            yield from item  # type: ignore[misc]  # items may themselves be non-scalar

    deeply_nested = [[1, [2, 3]], [4]]

    # yield from peels only one layer — inner lists remain intact
    result = list(flatten_one_level(deeply_nested))
    assert result == [1, [2, 3], 4]  # not [1, 2, 3, 4]


def test_yield_from_cannot_be_used_outside_a_function() -> None:
    # yield from (like yield) is only valid inside a function body
    with pytest.raises(SyntaxError):
        compile("yield from [1, 2, 3]", "<string>", "exec")
