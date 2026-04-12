# Generator expressions: lazy syntax, memory efficiency, pipeline patterns, pitfalls.

from collections.abc import Generator, Iterable
import itertools
import sys
import types

# ---------------------------------------------------------------------------
# 1. Generator expression syntax
# ---------------------------------------------------------------------------


def test_generator_expression_basic_syntax() -> None:
    list_comp = [x * 2 for x in range(5)]
    gen_expr = (x * 2 for x in range(5))

    assert list(gen_expr) == list_comp


def test_generator_expression_returns_generator_object_not_list() -> None:
    gen = (x for x in range(3))
    assert isinstance(gen, types.GeneratorType)
    assert not isinstance(gen, list)


def test_generator_expression_with_filter() -> None:
    evens_list = [x for x in range(10) if x % 2 == 0]
    evens_gen = (x for x in range(10) if x % 2 == 0)

    assert list(evens_gen) == evens_list


def test_nested_generator_expression() -> None:
    nested_list = [x * y for x in range(3) for y in range(3)]
    nested_gen = (x * y for x in range(3) for y in range(3))

    assert list(nested_gen) == nested_list


def test_generator_expression_parentheses_optional_as_sole_argument() -> None:
    result_with_parens = sum((x * x for x in range(5)))  # noqa: UP034 — teaching the with-parens form explicitly
    result_without_parens = sum(x * x for x in range(5))

    assert result_with_parens == result_without_parens == 30


# ---------------------------------------------------------------------------
# 2. Laziness and memory
# ---------------------------------------------------------------------------


def test_generator_expression_is_lazy() -> None:
    log: list[int] = []

    def logged(x: int) -> int:
        log.append(x)
        return x

    gen = (logged(x) for x in range(5))
    assert log == []  # nothing computed yet

    next(gen)
    assert log == [0]  # only the first element was computed


def test_generator_expression_is_smaller_than_list_comprehension() -> None:
    n = 10_000
    gen_size = sys.getsizeof(x for x in range(n))
    list_size = sys.getsizeof([x for x in range(n)])  # noqa: C416 — teaching list comprehension syntax for comparison

    # Generator is a fixed-size object; list scales with n
    assert gen_size < 500
    assert list_size > 40_000


def test_generator_expression_for_early_termination_saves_work() -> None:
    computed: list[int] = []

    def compute(x: int) -> int:
        computed.append(x)
        return x

    first_even_above_10 = next(compute(x) for x in range(100) if x > 10 and x % 2 == 0)

    assert first_even_above_10 == 12
    # Values 0-12 were evaluated (13 values), not all 100
    assert len(computed) <= 13


# ---------------------------------------------------------------------------
# 3. Practical patterns
# ---------------------------------------------------------------------------


def test_chaining_generator_expressions_as_a_pipeline() -> None:
    numbers = range(10)
    evens = (x for x in numbers if x % 2 == 0)
    squared = (x * x for x in evens)

    # Nothing is computed until the final stage is consumed
    result = list(squared)
    assert result == [0, 4, 16, 36, 64]


def test_generator_expression_in_sum_max_min() -> None:
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    assert sum(x * x for x in data) == 173
    assert max(abs(x) for x in [-3, 1, -7, 4]) == 7
    assert min(len(s) for s in ["hello", "hi", "hey"]) == 2


def test_any_and_all_short_circuit_on_generator_expressions() -> None:
    checked: list[int] = []

    def check(x: int) -> bool:
        checked.append(x)
        return x > 0

    # any() stops at the first True — does not consume the rest of the generator
    result = any(check(x) for x in [-1, -2, 3, 4, 5])
    assert result is True
    assert checked == [-1, -2, 3]  # stopped after confirming 3 > 0


def test_generator_expression_with_itertools_islice() -> None:
    # islice safely takes N values from a long or infinite genexpr
    first_five_squares = list(itertools.islice((x * x for x in range(1_000_000)), 5))
    assert first_five_squares == [0, 1, 4, 9, 16]


def test_custom_function_accepting_iterable_works_with_generator_expressions() -> None:
    # Any function typed as Iterable[T] transparently accepts a generator expression —
    # the caller passes the genexpr without wrapping it in list() first.
    def count_above(values: Iterable[int], threshold: int) -> int:
        """Return how many values exceed the threshold."""
        total = 0
        for value in values:
            if value > threshold:
                total += 1
        return total

    # Calling with a generator expression — nothing is materialised into a list
    result = count_above((x * x for x in range(6)), threshold=10)
    assert result == 2  # 16 (4²) and 25 (5²) exceed 10

    # The same function also accepts lists, ranges, or any other iterable
    assert count_above([1, 5, 3, 8], threshold=4) == 2
    assert count_above(range(10), threshold=7) == 2


def test_generator_function_accepting_iterable_yields_filtered_values() -> None:
    # The consumer can itself be a generator — it pulls from Iterable[T] lazily
    # and yields matching values one by one, keeping the whole pipeline lazy.
    def above_threshold(values: Iterable[int], threshold: int) -> Generator[int]:
        for value in values:
            if value > threshold:
                yield value

    result = list(above_threshold((x * x for x in range(6)), threshold=10))
    assert result == [16, 25]  # 4² and 5² are the only squares above 10

    # Laziness is preserved end-to-end: the genexpr feeds into the generator
    # one element at a time — no intermediate list is created at any stage.
    first = next(above_threshold((x * x for x in range(10)), threshold=50))
    assert first == 64  # 8² — stops after finding the first match


# ---------------------------------------------------------------------------
# 4. Pitfalls
# ---------------------------------------------------------------------------


def test_generator_expression_is_exhausted_after_one_pass() -> None:
    gen = (x for x in range(5))
    first_pass = list(gen)
    second_pass = list(gen)

    assert first_pass == [0, 1, 2, 3, 4]
    assert second_pass == []  # silently empty — not an error, easy to miss


def test_generator_expression_iterable_is_evaluated_eagerly_at_creation() -> None:
    source = [1, 2, 3]
    gen = (x for x in source)
    source = [4, 5, 6]  # reassign — but the genexpr already captured the original list

    # The original list object is iterated, not the new one
    assert list(gen) == [1, 2, 3]


def test_generator_expression_free_variable_is_looked_up_lazily() -> None:
    multiplier = 2
    gen = (x * multiplier for x in range(3))
    multiplier = 10  # reassign after genexpr creation

    # The element expression is evaluated at iteration time, not at creation
    result = list(gen)
    assert result == [0, 10, 20]  # not [0, 2, 4]


def test_generator_expression_not_suitable_when_multiple_passes_needed() -> None:
    gen = (x * x for x in range(5))
    first = list(gen)
    second = list(gen)

    assert first == [0, 1, 4, 9, 16]
    assert second == []  # generator is gone after the first pass

    # Solution: convert to list up front when re-iteration is needed
    cached = list(x * x for x in range(5))  # noqa: C400 — showing list() to cache a genexpr
    assert list(cached) == list(cached) == [0, 1, 4, 9, 16]
