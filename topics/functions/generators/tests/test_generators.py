# Generator functions, lazy evaluation, the iterator protocol, and internals.

from collections.abc import Generator
import inspect
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def counting_up(start: int, stop: int) -> Generator[int]:
    current = start
    while current < stop:
        yield current
        current += 1


def fibonacci() -> Generator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# ---------------------------------------------------------------------------
# 1. Generator function basics
# ---------------------------------------------------------------------------


def test_function_with_yield_is_a_generator_function() -> None:
    def gen() -> Generator[int]:
        yield 1

    # Calling the function returns a generator object — the body has not run yet
    result = gen()
    assert isinstance(result, types.GeneratorType)


def test_generator_function_body_does_not_run_on_call() -> None:
    log: list[str] = []

    def gen() -> Generator[int]:
        log.append("started")
        yield 1

    gen()  # calling does not execute the body
    assert log == []


def test_each_call_creates_independent_generator() -> None:
    gen_a = counting_up(0, 3)
    gen_b = counting_up(0, 3)

    assert gen_a is not gen_b
    next(gen_a)  # advance gen_a by one
    assert next(gen_b) == 0  # gen_b is unaffected


def test_generator_with_no_yield_raises_stopiteration_immediately() -> None:
    # A generator whose reachable code never hits a yield exhausts immediately.
    def gen() -> Generator[int]:
        if False:  # dead branch — yield present to make this a generator function
            yield 0

    instance = gen()
    assert isinstance(instance, types.GeneratorType)
    with pytest.raises(StopIteration):
        next(instance)


def test_generator_type_is_types_generatortype() -> None:
    gen = counting_up(0, 1)
    assert isinstance(gen, types.GeneratorType)
    assert isinstance(gen, Generator)  # also satisfies the collections.abc ABC


def test_generator_object_is_an_iterator() -> None:
    gen = counting_up(0, 3)
    assert hasattr(gen, "__iter__")
    assert hasattr(gen, "__next__")


def test_generator_object_is_its_own_iterable() -> None:
    gen = counting_up(0, 3)
    # iter(gen) returns the same object — generators are self-iterating
    assert iter(gen) is gen


# ---------------------------------------------------------------------------
# 2. Yield and lazy evaluation
# ---------------------------------------------------------------------------


def test_next_resumes_execution_from_last_yield() -> None:
    log: list[str] = []

    def gen() -> Generator[int]:
        log.append("A")
        yield 1
        log.append("B")
        yield 2

    instance = gen()
    assert next(instance) == 1
    assert log == ["A"]  # only ran up to the first yield

    assert next(instance) == 2
    assert log == ["A", "B"]  # then ran up to the second yield


def test_generator_preserves_local_variable_state_between_yields() -> None:
    def counter() -> Generator[int]:
        count = 0
        yield count
        count += 1
        yield count
        count += 1
        yield count

    gen = counter()
    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 2


def test_generator_produces_values_on_demand_not_all_at_once() -> None:
    log: list[str] = []

    def gen() -> Generator[int]:
        log.append("before first yield")
        yield 1
        log.append("before second yield")
        yield 2

    instance = gen()
    assert log == []  # body hasn't run at all

    next(instance)
    assert log == ["before first yield"]  # ran only to the first yield

    next(instance)
    assert log == ["before first yield", "before second yield"]


def test_for_loop_drives_generator_via_next() -> None:
    result_via_for = list(counting_up(0, 3))

    gen = counting_up(0, 3)
    result_via_next: list[int] = []
    while True:
        try:
            result_via_next.append(next(gen))
        except StopIteration:
            break

    assert result_via_for == result_via_next == [0, 1, 2]


def test_generator_raises_stopiteration_after_last_yield() -> None:
    gen = counting_up(0, 2)
    next(gen)  # 0
    next(gen)  # 1
    with pytest.raises(StopIteration):
        next(gen)


def test_generator_is_exhausted_after_stopiteration() -> None:
    gen = counting_up(0, 2)
    list(gen)  # exhaust it
    # Re-iterating silently returns nothing — no error, no reset
    assert list(gen) == []


def test_return_value_sets_stopiteration_value() -> None:
    def gen_with_return() -> Generator[int, None, str]:
        yield 1
        return "finished"  # sets StopIteration.value

    instance = gen_with_return()
    next(instance)
    with pytest.raises(StopIteration) as exc_info:
        next(instance)
    assert exc_info.value.value == "finished"


def test_yield_with_no_operand_produces_none() -> None:
    def gen() -> Generator[None]:
        yield
        yield
        yield

    instance = gen()
    # yield with no operand produces None — distinct from exhaustion
    assert next(instance) is None
    assert next(instance) is None
    assert next(instance) is None


# ---------------------------------------------------------------------------
# 3. Protocol internals
# ---------------------------------------------------------------------------


def test_gi_frame_is_not_none_before_exhaustion() -> None:
    gen = counting_up(0, 3)
    next(gen)
    # The suspended frame is kept alive while the generator has values left
    assert gen.gi_frame is not None  # type: ignore[attr-defined]  # CPython implementation attribute


def test_gi_frame_is_none_after_exhaustion() -> None:
    gen = counting_up(0, 1)
    list(gen)
    # Frame is released once the generator is finished
    assert gen.gi_frame is None  # type: ignore[attr-defined]  # CPython implementation attribute


def test_gi_running_is_false_outside_next_call() -> None:
    running_states: list[bool] = []

    def gen() -> Generator[None]:
        # gi_running is True while CPython is executing this frame
        running_states.append(instance.gi_running)  # type: ignore[attr-defined]
        yield

    instance = gen()
    assert instance.gi_running is False  # type: ignore[attr-defined]  # not running yet

    next(instance)

    assert instance.gi_running is False  # type: ignore[attr-defined]  # not running after next() returns
    assert running_states == [True]  # was True while inside the frame


def test_inspect_isgenerator_identifies_generator_objects() -> None:
    gen = counting_up(0, 3)
    assert inspect.isgenerator(gen) is True
    assert inspect.isgenerator([1, 2, 3]) is False
    assert inspect.isgenerator(iter([1, 2, 3])) is False


def test_inspect_isgeneratorfunction_identifies_generator_functions() -> None:
    assert inspect.isgeneratorfunction(counting_up) is True
    assert inspect.isgeneratorfunction(list) is False
    assert inspect.isgeneratorfunction(lambda: None) is False


def test_generator_cannot_be_restarted_after_exhaustion() -> None:
    gen = counting_up(0, 2)
    list(gen)

    # Exhausted generators stay exhausted — calling next() always raises StopIteration
    with pytest.raises(StopIteration):
        next(gen)
    with pytest.raises(StopIteration):
        next(gen)


# ---------------------------------------------------------------------------
# 4. When to use generators
# ---------------------------------------------------------------------------


def test_generator_is_preferable_for_large_sequences() -> None:
    large_n = 100_000
    gen = counting_up(0, large_n)
    gen_size = sys.getsizeof(gen)

    full_list = list(range(large_n))
    list_size = sys.getsizeof(full_list)

    # Generator object is a fixed ~200 bytes regardless of n
    assert gen_size < 500
    # List grows proportionally — 100k pointers at 8 bytes each plus overhead
    assert list_size > 400_000


def test_generator_enables_infinite_sequences() -> None:
    # Infinite sequences are impossible with lists; generators handle them naturally
    gen = fibonacci()
    first_ten = [next(gen) for _ in range(10)]
    assert first_ten == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_generator_enables_early_exit_without_computing_all_values() -> None:
    computed: list[int] = []

    def expensive_sequence() -> Generator[int]:
        for i in range(1000):
            computed.append(i)  # stands in for an expensive computation
            yield i

    # Stops as soon as a match is found — no wasted work
    first_above_five = next(x for x in expensive_sequence() if x > 5)

    assert first_above_five == 6
    assert len(computed) == 7  # only 0-6 were evaluated, not all 1000


# ---------------------------------------------------------------------------
# 5. Pitfalls
# ---------------------------------------------------------------------------


def test_forgetting_to_call_generator_function_is_a_common_mistake() -> None:
    # Passing the function object instead of calling it is not iterable
    with pytest.raises(TypeError):
        list(counting_up)  # type: ignore[call-overload]  # missing () is intentional to show the mistake


def test_generator_exhaustion_is_silent_in_a_for_loop() -> None:
    gen = counting_up(0, 3)
    first_pass = list(gen)
    assert first_pass == [0, 1, 2]

    # Re-iterating an exhausted generator silently yields nothing — no error raised
    second_pass = list(gen)
    assert second_pass == []


def test_generator_is_not_reusable_like_a_list() -> None:
    gen = counting_up(0, 3)

    # Wrap in list() to cache when multiple passes are needed
    cached = list(gen)
    assert list(cached) == [0, 1, 2]
    assert list(cached) == [0, 1, 2]  # reusable

    # The generator itself is now permanently exhausted
    assert list(gen) == []
