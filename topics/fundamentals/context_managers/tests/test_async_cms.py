# Async context managers as pytest-verified learning notes.
# Covers: __aenter__/__aexit__ protocol, async with, @asynccontextmanager.
#
# Advanced async patterns (trio, anyio, structured concurrency, TaskGroup, etc.):
#   topics/asyncio/ (upcoming, @TODO)

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import types
from typing import Self

import pytest

# ---------------------------------------------------------------------------
# __aenter__ / __aexit__ protocol
# ---------------------------------------------------------------------------


async def test_aenter_aexit_called_by_async_with() -> None:
    # async with calls __aenter__ on entry and __aexit__ on exit, just like
    # the sync protocol — but both must be async def (awaitable)
    entered = False
    exited = False

    class AsyncCM:
        async def __aenter__(self) -> Self:
            nonlocal entered
            entered = True
            return self

        async def __aexit__(self, *args: object) -> None:
            nonlocal exited
            exited = True

    async with AsyncCM():
        assert entered is True

    assert exited is True


async def test_async_with_binds_aenter_return_value() -> None:
    # 'as' binds whatever __aenter__ returns — same rule as the sync protocol
    class AsyncCM:
        async def __aenter__(self) -> str:
            return "hello"

        async def __aexit__(self, *args: object) -> None:
            pass

    async with AsyncCM() as val:
        assert val == "hello"


async def test_aexit_receives_none_args_on_clean_exit() -> None:
    # On a clean exit __aexit__ is called with (None, None, None)
    exit_args: tuple[object, object, object] = ("unset", "unset", "unset")

    class AsyncCM:
        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc_val: object,
            exc_tb: object,
        ) -> None:
            nonlocal exit_args
            exit_args = (exc_type, exc_val, exc_tb)

    async with AsyncCM():
        pass

    assert exit_args == (None, None, None)


async def test_aexit_receives_exception_info_on_error() -> None:
    # When the body raises, __aexit__ receives (type, value, traceback)
    captured: list[object] = []

    class AsyncCM:
        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: object,
        ) -> None:
            captured.extend([exc_type, exc_val, exc_tb])

    with pytest.raises(ValueError):
        async with AsyncCM():
            raise ValueError("async body error")

    assert captured[0] is ValueError
    assert isinstance(captured[1], ValueError)
    assert isinstance(captured[2], types.TracebackType)


async def test_aexit_returning_true_suppresses_exception() -> None:
    # Returning True from __aexit__ suppresses the exception — same as sync
    class Suppressor:
        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, *args: object) -> bool:
            return True

    result: list[str] = []
    async with Suppressor():
        raise ValueError("swallowed")
    result.append("after")
    assert result == ["after"]


# ---------------------------------------------------------------------------
# @asynccontextmanager
# ---------------------------------------------------------------------------


async def test_asynccontextmanager_basic_setup_and_teardown() -> None:
    # @asynccontextmanager mirrors @contextmanager but uses an async generator.
    # Code before yield runs on enter; code after runs on exit.
    log: list[str] = []

    @asynccontextmanager
    async def managed() -> AsyncGenerator[str]:
        log.append("enter")
        yield "resource"
        log.append("exit")

    async with managed() as value:
        assert value == "resource"
        log.append("body")

    assert log == ["enter", "body", "exit"]


async def test_asynccontextmanager_cleanup_runs_on_exception() -> None:
    # A finally block after yield is guaranteed to run even when the body raises
    cleaned: list[bool] = []

    @asynccontextmanager
    async def managed() -> AsyncGenerator[None]:
        try:
            yield
        finally:
            cleaned.append(True)

    with pytest.raises(RuntimeError):
        async with managed():
            raise RuntimeError("boom")

    assert cleaned == [True]


async def test_asynccontextmanager_can_suppress_exception() -> None:
    # The async generator can catch the re-thrown exception to suppress it
    @asynccontextmanager
    async def suppress_value_errors() -> AsyncGenerator[None]:
        try:  # noqa: SIM105 — intentional: showing generator-level suppression
            yield
        except ValueError:
            pass

    result: list[str] = []
    async with suppress_value_errors():
        raise ValueError("suppressed")
    result.append("after")
    assert result == ["after"]
