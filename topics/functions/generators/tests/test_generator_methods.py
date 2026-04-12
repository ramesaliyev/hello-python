# Generator methods: send() for two-way communication, throw() for injecting exceptions,
# close() and GeneratorExit for explicit termination.

from collections.abc import Generator
import gc

import pytest

# ---------------------------------------------------------------------------
# 1. send() — mechanics
# ---------------------------------------------------------------------------


def test_send_none_is_equivalent_to_next() -> None:
    def gen() -> Generator[int]:
        yield 0
        yield 1
        yield 2

    instance = gen()
    # send(None) on an unstarted generator is identical to next().
    # Convention: always use next() for priming — it signals "advance to the first
    # yield" without implying data is being sent. Use send(value) only for two-way
    # communication.
    assert instance.send(None) == 0
    assert instance.send(None) == 1


def test_send_before_first_yield_requires_none() -> None:
    def gen() -> Generator[int, int]:
        value = yield 0
        yield value * 2

    instance = gen()
    with pytest.raises(
        TypeError, match="can't send non-None value to a just-started generator"
    ):
        instance.send(10)


def test_send_value_is_result_of_yield_expression() -> None:
    received: list[int] = []

    def gen() -> Generator[str, int]:
        while True:
            # yield is an expression — its value is whatever was sent()
            value = yield "ready"
            received.append(value)

    instance = gen()
    next(instance)  # prime: advance to first yield
    instance.send(42)
    instance.send(100)

    assert received == [42, 100]


def test_send_return_value_is_the_next_yielded_value() -> None:
    def gen() -> Generator[int]:
        yield 10
        yield 20
        yield 30

    instance = gen()
    # send() returns the value yielded by the next yield statement, just like next()
    assert instance.send(None) == 10
    assert instance.send(None) == 20


def test_send_none_after_started_is_safe() -> None:
    def gen() -> Generator[int]:
        yield 1
        yield 2
        yield 3

    instance = gen()
    next(instance)  # prime — advances to yield 1
    # After priming, send(None) and next() are interchangeable
    assert instance.send(None) == 2
    assert next(instance) == 3


# ---------------------------------------------------------------------------
# 2. send() — patterns
# ---------------------------------------------------------------------------


def test_send_drives_a_running_average_accumulator() -> None:
    def running_average() -> Generator[float, float]:
        """Receives numbers, yields the running average after each one."""
        total = 0.0
        count = 0
        while True:
            value = yield (total / count if count > 0 else 0.0)
            total += value
            count += 1

    gen = running_average()
    next(gen)  # prime
    assert gen.send(10.0) == 10.0
    assert gen.send(20.0) == 15.0
    assert gen.send(30.0) == 20.0


def test_generator_as_coroutine_pipeline() -> None:
    results: list[str] = []

    def printer() -> Generator[None, str | None]:
        """Receives strings and stores them uppercased."""
        while True:
            word = yield
            if word is None:
                return
            results.append(word.upper())

    def feed(consumer: Generator[None, str | None], words: list[str]) -> None:
        next(consumer)  # prime
        for word in words:
            consumer.send(word)

    sink = printer()
    feed(sink, ["hello", "world", "python"])
    assert results == ["HELLO", "WORLD", "PYTHON"]


# ---------------------------------------------------------------------------
# 3. throw() — mechanics
# ---------------------------------------------------------------------------


def test_throw_raises_exception_at_yield_point() -> None:
    def gen() -> Generator[int]:
        yield 1
        yield 2

    instance = gen()
    next(instance)

    with pytest.raises(ValueError, match="injected"):
        instance.throw(ValueError("injected"))


def test_throw_can_be_caught_inside_generator() -> None:
    caught_messages: list[str] = []

    def gen() -> Generator[int]:
        while True:
            try:
                yield 1
            except ValueError as exc:
                caught_messages.append(str(exc))
                yield -1

    instance = gen()
    assert next(instance) == 1
    assert instance.throw(ValueError("oops")) == -1
    assert caught_messages == ["oops"]


def test_throw_on_exhausted_generator_propagates_the_thrown_exception() -> None:
    def gen() -> Generator[int]:
        yield 1

    instance = gen()
    list(instance)  # exhaust

    # Throwing into an exhausted generator has no frame to handle it —
    # the exception propagates directly to the caller
    with pytest.raises(ValueError, match="too late"):
        instance.throw(ValueError("too late"))


def test_throw_uncaught_exception_propagates_to_caller() -> None:
    def gen() -> Generator[int]:
        yield 1
        yield 2

    instance = gen()
    next(instance)

    with pytest.raises(RuntimeError, match="boom"):
        instance.throw(RuntimeError("boom"))


# ---------------------------------------------------------------------------
# 4. throw() — patterns
# ---------------------------------------------------------------------------


def test_throw_generator_can_yield_after_catching_thrown_exception() -> None:
    def gen() -> Generator[int]:
        try:
            yield 1
        except ValueError:
            yield 2  # catching the exception lets the generator continue
        yield 3

    instance = gen()
    assert next(instance) == 1
    assert instance.throw(ValueError()) == 2
    assert next(instance) == 3


def test_throw_used_to_signal_cancellation_to_generator() -> None:
    class Cancelled(Exception):  # noqa: N818 — Cancelled signals a domain concept, not a programming error
        pass

    cleanup_ran: list[bool] = []

    def long_running() -> Generator[int]:
        try:
            for i in range(100):  # noqa: UP028 — for/yield needed so throw() targets this frame's handler
                yield i
        except Cancelled:
            cleanup_ran.append(True)
            # generator ends here — no more yields after catching Cancelled

    instance = long_running()
    next(instance)
    next(instance)

    # Inject Cancelled to stop the generator and trigger cleanup
    with pytest.raises(StopIteration):
        instance.throw(Cancelled())

    assert cleanup_ran == [True]


# ---------------------------------------------------------------------------
# 5. close() and GeneratorExit — mechanics
# ---------------------------------------------------------------------------


def test_close_injects_generator_exit_at_yield_point() -> None:
    exit_received: list[bool] = []

    def gen() -> Generator[int]:
        try:
            yield 1
        except GeneratorExit:
            exit_received.append(True)
            raise  # must re-raise — yielding inside this handler raises RuntimeError

    instance = gen()
    next(instance)
    instance.close()

    assert exit_received == [True]


def test_gi_frame_is_none_after_close() -> None:
    def gen() -> Generator[int]:
        yield 1

    instance = gen()
    next(instance)
    assert instance.gi_frame is not None  # type: ignore[attr-defined]

    instance.close()
    assert instance.gi_frame is None  # type: ignore[attr-defined]


def test_close_on_exhausted_generator_is_a_noop() -> None:
    def gen() -> Generator[int]:
        yield 1

    instance = gen()
    list(instance)
    instance.close()  # should not raise


def test_close_on_unstarted_generator_is_a_noop() -> None:
    def gen() -> Generator[int]:
        yield 1

    instance = gen()
    instance.close()  # should not raise


def test_generator_finally_block_runs_on_close() -> None:
    cleanup_log: list[str] = []

    def gen() -> Generator[int]:
        try:
            yield 1
            yield 2
        finally:
            cleanup_log.append("cleanup")  # guaranteed to run even on close()

    instance = gen()
    next(instance)
    instance.close()

    assert cleanup_log == ["cleanup"]


def test_del_on_generator_triggers_close() -> None:
    cleanup_ran: list[bool] = []

    def gen() -> Generator[int]:
        try:
            yield 1
        finally:
            cleanup_ran.append(True)

    instance = gen()
    next(instance)
    del instance
    gc.collect()  # ensure CPython finalizer runs deterministically

    assert cleanup_ran == [True]


# ---------------------------------------------------------------------------
# 6. Pitfalls
# ---------------------------------------------------------------------------


def test_generator_cannot_yield_inside_generator_exit_handler() -> None:
    def gen() -> Generator[int]:
        try:
            yield 1
        except GeneratorExit:
            yield 2  # illegal — cannot yield while handling GeneratorExit

    instance = gen()
    next(instance)
    with pytest.raises(RuntimeError):
        instance.close()


def test_generator_can_raise_different_exception_from_generator_exit_handler() -> None:
    def gen() -> Generator[int]:
        try:
            yield 1
        except GeneratorExit:
            raise RuntimeError("cleanup failed") from None

    instance = gen()
    next(instance)
    # The new exception propagates out of close() to the caller
    with pytest.raises(RuntimeError, match="cleanup failed"):
        instance.close()


def test_forgetting_to_prime_generator_before_send_is_a_common_mistake() -> None:
    def accumulator() -> Generator[float, float]:
        total = 0.0
        while True:
            value = yield total
            total += value

    instance = accumulator()

    # Common mistake: sending a value before priming raises TypeError
    with pytest.raises(
        TypeError, match="can't send non-None value to a just-started generator"
    ):
        instance.send(10.0)

    # Correct pattern: prime with next() or send(None) first
    instance2 = accumulator()
    initial = next(instance2)  # prime — advances to the first yield
    assert initial == 0.0
    assert instance2.send(10.0) == 10.0
