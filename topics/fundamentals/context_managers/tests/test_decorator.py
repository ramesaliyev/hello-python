# @contextmanager decorator as pytest-verified learning notes.

from collections.abc import Generator
from contextlib import contextmanager

import pytest

# ---------------------------------------------------------------------------
# @contextmanager
# ---------------------------------------------------------------------------


def test_contextmanager_basic_setup_and_teardown() -> None:
    # @contextmanager: code before yield runs on enter, code after runs on exit
    log: list[str] = []

    @contextmanager
    def managed() -> Generator[str]:
        log.append("enter")
        yield "resource"
        log.append("exit")

    with managed() as value:
        assert value == "resource"
        log.append("body")

    assert log == ["enter", "body", "exit"]


def test_contextmanager_yield_value_is_the_as_variable() -> None:
    # The value passed to yield becomes the 'as' variable in the with statement
    @contextmanager
    def provide() -> Generator[int]:
        yield 42

    with provide() as val:
        assert val == 42


def test_contextmanager_cleanup_runs_on_exception() -> None:
    # Code in a finally block after yield still runs even if the body raises
    cleaned: list[bool] = []

    @contextmanager
    def managed() -> Generator[None]:
        try:
            yield
        finally:
            cleaned.append(True)  # guaranteed to run

    with pytest.raises(RuntimeError), managed():
        raise RuntimeError("boom")

    assert cleaned == [True]


def test_contextmanager_can_suppress_exception() -> None:
    # The generator can catch the exception re-thrown at the yield point to suppress it
    @contextmanager
    def suppress_value_errors() -> Generator[None]:
        try:  # noqa: SIM105 — intentional: showing how generators suppress at the yield point
            yield
        except ValueError:
            pass

    result: list[str] = []
    with suppress_value_errors():
        raise ValueError("suppressed")
    result.append("after")
    assert result == ["after"]


def test_contextmanager_double_yield_raises_runtime_error() -> None:
    # A @contextmanager generator must yield exactly once; yielding twice is an error
    @contextmanager
    def bad_cm() -> Generator[int]:
        yield 1
        yield 2  # second yield — __exit__ raises RuntimeError

    with pytest.raises(RuntimeError, match="didn't stop"), bad_cm():
        pass


# ---------------------------------------------------------------------------
# @contextmanager used as a function decorator
# ---------------------------------------------------------------------------


def test_contextmanager_used_as_decorator() -> None:
    # @contextmanager functions also work as function decorators via ContextDecorator.
    # The decorated function is wrapped so each call runs inside a fresh CM instance.
    log: list[str] = []

    @contextmanager
    def managed() -> Generator[None]:
        log.append("enter")
        yield
        log.append("exit")

    @managed()
    def work() -> None:
        log.append("body")

    work()
    assert log == ["enter", "body", "exit"]

    log.clear()
    work()  # second call creates a fresh generator — the CM is not exhausted
    assert log == ["enter", "body", "exit"]


def test_contextmanager_decorator_wraps_return_value() -> None:
    # The wrapped function still returns its original return value
    @contextmanager
    def managed() -> Generator[None]:
        yield

    @managed()
    def compute() -> int:
        return 42

    assert compute() == 42
