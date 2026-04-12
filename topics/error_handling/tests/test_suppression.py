# Suppressing exceptions via context managers as pytest-verified learning notes.

from contextlib import suppress

import pytest

# ---------------------------------------------------------------------------
# contextlib.suppress
# ---------------------------------------------------------------------------


def test_suppress_silences_specified_exception() -> None:
    # suppress() is a context manager that swallows the listed exception types
    with suppress(ValueError):
        raise ValueError("ignored")
    # Execution continues here as if nothing happened


def test_suppress_allows_code_after_with_block_to_run() -> None:
    # After suppressing an exception, everything after the with block runs normally
    result = []
    with suppress(ValueError):
        raise ValueError("x")
    result.append("after")
    assert result == ["after"]


def test_suppress_multiple_exception_types() -> None:
    # suppress accepts multiple types — any of them is silenced
    for exc in [ValueError("v"), TypeError("t")]:
        with suppress(ValueError, TypeError):
            raise exc  # both are swallowed


def test_suppress_does_not_catch_unrelated_exception() -> None:
    # Exceptions not listed in suppress() still propagate normally
    with pytest.raises(KeyError), suppress(ValueError):
        raise KeyError("not suppressed")


def test_suppress_with_no_exception_is_a_noop() -> None:
    # suppress() is transparent when no exception occurs
    result = []
    with suppress(ValueError):
        result.append(1)
    assert result == [1]


def test_suppress_as_idiomatic_try_except_pass() -> None:
    # contextlib.suppress is the idiomatic replacement for try/except: pass
    result = []

    # Verbose style — common but noisy:
    try:  # noqa: SIM105 — intentional: showing verbose style before the idiomatic alternative
        result.append(int("not a number"))
    except ValueError:
        pass

    # Idiomatic style — same semantics, less boilerplate:
    with suppress(ValueError):
        result.append(int("not a number"))  # int() fails, suppress swallows it

    assert result == []  # neither attempt appended anything


# ---------------------------------------------------------------------------
# __exit__ returning True to suppress exceptions
# ---------------------------------------------------------------------------


class _SuppressorCM:
    """Context manager that suppresses all exceptions via __exit__ returning True."""

    def __init__(self) -> None:
        self.caught_type: type | None = None
        self.caught_val: BaseException | None = None

    def __enter__(self) -> _SuppressorCM:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> bool:
        self.caught_type = exc_type
        self.caught_val = exc_val
        return True  # True = suppress; None/False = propagate


class _PropagatorCM:
    """Context manager that lets all exceptions through."""

    def __enter__(self) -> _PropagatorCM:
        return self

    def __exit__(self, *args: object) -> None:
        pass  # returning None propagates the exception


def test_exit_returning_true_suppresses_exception() -> None:
    # __exit__ is the protocol-level hook for suppression: return True to swallow
    cm = _SuppressorCM()
    with cm:
        raise ValueError("swallowed")
    # No exception escaped — and we can inspect what was caught
    assert cm.caught_type is ValueError
    assert str(cm.caught_val) == "swallowed"


def test_exit_returning_false_propagates_exception() -> None:
    # Returning False (or None) from __exit__ does not suppress — exception propagates
    with pytest.raises(ValueError), _PropagatorCM():
        raise ValueError("propagated")


def test_exit_receives_none_when_no_exception() -> None:
    # When no exception occurs, __exit__ is called with (None, None, None)
    cm = _SuppressorCM()
    with cm:
        pass
    assert cm.caught_type is None
    assert cm.caught_val is None


def test_exit_receives_exception_type_and_value() -> None:
    # __exit__ receives the full exception triple: (type, value, traceback)
    cm = _SuppressorCM()
    with cm:
        raise RuntimeError("info")
    assert cm.caught_type is RuntimeError
    assert isinstance(cm.caught_val, RuntimeError)


# ---------------------------------------------------------------------------
# Practical patterns
# ---------------------------------------------------------------------------


def test_suppress_for_best_effort_cleanup() -> None:
    # A common pattern: suppress errors from cleanup that may legitimately fail
    cleaned: list[str] = []

    def maybe_cleanup(item: str) -> None:
        if item == "missing":
            raise FileNotFoundError(item)
        cleaned.append(item)

    items = ["file1", "missing", "file2"]
    for item in items:
        with suppress(FileNotFoundError):
            maybe_cleanup(item)

    assert cleaned == ["file1", "file2"]  # "missing" was skipped, not crashed


def test_selective_suppression_via_exit_inspection() -> None:
    # __exit__ can inspect exc_type to implement conditional suppression
    class SelectiveCM:
        def __init__(self, *suppress_types: type) -> None:
            self.suppress_types = suppress_types

        def __enter__(self) -> SelectiveCM:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: object,
        ) -> bool:
            if exc_type is not None:
                return issubclass(exc_type, self.suppress_types)
            return False

    with SelectiveCM(ValueError):
        raise ValueError("suppressed")

    with pytest.raises(TypeError), SelectiveCM(ValueError):
        raise TypeError("not suppressed")
