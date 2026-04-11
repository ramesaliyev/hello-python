# Context manager protocol (__enter__ / __exit__) as pytest-verified learning notes.

from collections.abc import Generator
from contextlib import contextmanager
import types
from typing import Self

import pytest

# Module-level alias for the __exit__ argument triple (type, value, traceback)
_ExitArgs = tuple[type[BaseException] | None, BaseException | None, object]

# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


class TrackedCM:
    """Records all enter/exit activity including any exception info."""

    def __init__(self, name: str = "cm") -> None:
        self.name = name
        self.entered = False
        self.exited = False
        self.exit_args: _ExitArgs = (None, None, None)

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.exited = True
        self.exit_args = (exc_type, exc_val, exc_tb)


# ---------------------------------------------------------------------------
# __enter__ / __exit__ protocol
# ---------------------------------------------------------------------------


def test_enter_called_when_entering_with_block() -> None:
    # __enter__ is invoked automatically when execution enters the with block
    cm = TrackedCM()
    with cm:
        assert cm.entered is True


def test_exit_called_when_leaving_with_block() -> None:
    # __exit__ is invoked automatically when execution leaves the with block
    cm = TrackedCM()
    with cm:
        pass
    assert cm.exited is True


def test_as_binds_enter_return_value_not_the_cm_itself() -> None:
    # 'as x' binds whatever __enter__ returns — not the context manager object
    # This is a common source of confusion
    class ReturnsString:
        def __enter__(self) -> str:
            return "not self"

        def __exit__(self, *args: object) -> None:
            pass

    with ReturnsString() as value:
        assert value == "not self"
        assert not isinstance(value, ReturnsString)


def test_enter_return_self_gives_access_to_cm_state() -> None:
    # When __enter__ returns self, 'as ctx' lets callers interact with the CM
    with TrackedCM() as ctx:
        assert ctx.entered is True
        assert isinstance(ctx, TrackedCM)


def test_exit_receives_none_args_on_clean_exit() -> None:
    # When no exception occurs, __exit__ is called with (None, None, None)
    cm = TrackedCM()
    with cm:
        pass
    assert cm.exit_args == (None, None, None)


def test_exit_receives_exception_info_on_error() -> None:
    # When an exception is raised, __exit__ receives (type, value, traceback)
    cm = TrackedCM()
    with pytest.raises(ValueError), cm:
        raise ValueError("test")
    exc_type, exc_val, exc_tb = cm.exit_args
    assert exc_type is ValueError
    assert isinstance(exc_val, ValueError)
    assert isinstance(exc_tb, types.TracebackType)


def test_exit_returning_none_propagates_exception() -> None:
    # Returning None (or False) from __exit__ does not suppress the exception
    with pytest.raises(ValueError), TrackedCM():
        raise ValueError("propagated")


def test_exit_returning_true_suppresses_exception() -> None:
    # Returning True from __exit__ swallows the exception; code after with still runs
    class Suppressor:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> bool:
            return True  # suppress

    result: list[str] = []
    with Suppressor():
        raise ValueError("swallowed")
    result.append("after")
    assert result == ["after"]


# ---------------------------------------------------------------------------
# Error edge cases
# ---------------------------------------------------------------------------


def test_enter_raising_skips_exit() -> None:
    # If __enter__ raises, __exit__ is never called — no active block to clean up
    exit_called = False

    class FailingEnter:
        def __enter__(self) -> None:
            raise RuntimeError("setup failed")

        def __exit__(self, *args: object) -> None:
            nonlocal exit_called
            exit_called = True

    with pytest.raises(RuntimeError, match="setup failed"), FailingEnter():
        pass

    assert exit_called is False


def test_exit_raising_masks_original_exception() -> None:
    # If __exit__ itself raises, its exception replaces the body exception.
    # The original body exception is preserved as __context__ on the new exception.
    class RaisingExit:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            raise RuntimeError("teardown failed")

    with (
        pytest.raises(RuntimeError, match="teardown failed") as exc_info,
        RaisingExit(),
    ):
        raise ValueError("body error")

    assert isinstance(exc_info.value.__context__, ValueError)


# ---------------------------------------------------------------------------
# Practical resource patterns
# ---------------------------------------------------------------------------


def test_context_manager_as_resource_guard() -> None:
    # A CM guarantees acquire/release of a resource even when the body raises
    acquired: list[str] = []
    released: list[str] = []

    @contextmanager
    def resource(name: str) -> Generator[str]:
        acquired.append(name)
        try:
            yield name
        finally:
            released.append(name)

    with resource("db") as db:
        assert db == "db"

    assert acquired == ["db"]
    assert released == ["db"]


def test_multiple_cms_equivalent_to_nested_with_blocks() -> None:
    # 'with A(), B():' is exactly the same as 'with A():\n    with B():'
    log: list[str] = []

    @contextmanager
    def cm(name: str) -> Generator[None]:
        log.append(f"enter:{name}")
        yield
        log.append(f"exit:{name}")

    with cm("outer"), cm("inner"):
        log.append("body")

    assert log == ["enter:outer", "enter:inner", "body", "exit:inner", "exit:outer"]
