# contextlib utilities as pytest-verified learning notes.
# Covers: suppress, closing, nullcontext, ExitStack.

from contextlib import AbstractContextManager, ExitStack, closing, nullcontext, suppress
from typing import Self

import pytest

# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


class TrackedCM:
    """Minimal CM that records whether it was entered and exited."""

    def __init__(self, name: str = "cm") -> None:
        self.name = name
        self.entered = False
        self.exited = False

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, *args: object) -> None:
        self.exited = True


# ---------------------------------------------------------------------------
# contextlib.suppress
# ---------------------------------------------------------------------------
# Full suppression patterns and __exit__ mechanics:
#   topics/error_handling/tests/test_suppression.py


def test_suppress_silences_specified_exception() -> None:
    # suppress() is a context manager that swallows the listed exception types
    with suppress(ValueError):
        raise ValueError("ignored")
    # Execution continues here as if nothing happened


def test_suppress_multiple_types() -> None:
    # suppress accepts multiple types — any of them is silenced
    for exc in [ValueError("v"), TypeError("t")]:
        with suppress(ValueError, TypeError):
            raise exc  # both are swallowed


def test_suppress_does_not_catch_unlisted_exception() -> None:
    # Exceptions not listed in suppress() still propagate normally
    with pytest.raises(KeyError), suppress(ValueError):
        raise KeyError("not suppressed")


# ---------------------------------------------------------------------------
# contextlib.closing
# ---------------------------------------------------------------------------


def test_closing_calls_close_on_exit() -> None:
    # closing() wraps any object with a .close() method, calling it on exit.
    # Useful for resources that predate the CM protocol (old-style file-like objects).
    closed = False

    class Resource:
        def close(self) -> None:
            nonlocal closed
            closed = True

    with closing(Resource()):
        pass

    assert closed is True


def test_closing_calls_close_even_on_exception() -> None:
    # .close() is guaranteed to run even when the body raises
    closed = False

    class Resource:
        def close(self) -> None:
            nonlocal closed
            closed = True

    with pytest.raises(RuntimeError), closing(Resource()):
        raise RuntimeError("boom")

    assert closed is True


def test_closing_binds_resource_via_as() -> None:
    # 'as' binds the object passed to closing(), not the CM wrapper itself
    class Resource:
        def close(self) -> None:
            pass

    r = Resource()
    with closing(r) as res:
        assert res is r


# ---------------------------------------------------------------------------
# contextlib.nullcontext
# ---------------------------------------------------------------------------


def test_nullcontext_is_noop() -> None:
    # nullcontext() has no side effects on enter or exit
    result: list[str] = []
    with nullcontext():
        result.append("work")
    assert result == ["work"]


def test_nullcontext_yields_enter_result() -> None:
    # nullcontext(value) makes 'as' bind to that value
    with nullcontext(42) as val:
        assert val == 42


def test_nullcontext_default_enter_result_is_none() -> None:
    # Without an argument, nullcontext() yields None
    with nullcontext() as val:
        assert val is None


def test_nullcontext_as_optional_cm_pattern() -> None:
    # The canonical use: a function that accepts an optional CM uses nullcontext()
    # as the default, so the body always runs inside some CM without an if-branch.
    entered: list[str] = []
    exited: list[str] = []

    class LoggingCM:
        def __enter__(self) -> Self:
            entered.append("in")
            return self

        def __exit__(self, *args: object) -> None:
            exited.append("out")

    def process(cm: AbstractContextManager[object] | None = None) -> str:
        with cm if cm is not None else nullcontext():
            return "done"

    assert process() == "done"  # no CM; nullcontext; no side effects
    assert process(LoggingCM()) == "done"  # real CM is entered and exited
    assert entered == ["in"]
    assert exited == ["out"]


# ---------------------------------------------------------------------------
# contextlib.ExitStack
# ---------------------------------------------------------------------------


def test_exitstack_enters_and_exits_registered_cms() -> None:
    # enter_context() both enters a CM and registers its __exit__ for cleanup
    cm1, cm2 = TrackedCM("a"), TrackedCM("b")
    with ExitStack() as stack:
        stack.enter_context(cm1)
        stack.enter_context(cm2)
        assert cm1.entered
        assert cm2.entered

    assert cm1.exited
    assert cm2.exited


def test_exitstack_exit_order_is_lifo() -> None:
    # CMs are exited in reverse registration order (last in, first out)
    order: list[str] = []

    class NamedCM:
        def __init__(self, name: str) -> None:
            self.name = name

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            order.append(self.name)

    with ExitStack() as stack:
        stack.enter_context(NamedCM("first"))
        stack.enter_context(NamedCM("second"))
        stack.enter_context(NamedCM("third"))

    assert order == ["third", "second", "first"]


def test_exitstack_exits_all_even_on_exception() -> None:
    # All registered cleanups run even when the body raises
    cm1, cm2 = TrackedCM("a"), TrackedCM("b")
    with pytest.raises(RuntimeError), ExitStack() as stack:
        stack.enter_context(cm1)
        stack.enter_context(cm2)
        raise RuntimeError("boom")

    assert cm1.exited
    assert cm2.exited


def test_exitstack_callback() -> None:
    # stack.callback(fn) registers an arbitrary cleanup function (no CM needed)
    log: list[str] = []

    with ExitStack() as stack:
        stack.callback(log.append, "cleanup-a")
        stack.callback(log.append, "cleanup-b")

    # callbacks fire in LIFO order on exit
    assert log == ["cleanup-b", "cleanup-a"]


def test_exitstack_dynamic_number_of_cms() -> None:
    # ExitStack shines when the number of CMs is only known at runtime
    cms = [TrackedCM(str(i)) for i in range(5)]

    with ExitStack() as stack:
        for cm in cms:
            stack.enter_context(cm)

    assert all(cm.exited for cm in cms)


def test_exitstack_alongside_standalone_cms_for_extra_callbacks() -> None:
    # ExitStack can sit beside other CMs in the same 'with' statement.
    # The standalone CMs manage their own __exit__; ExitStack only handles
    # whatever you explicitly register with it (callbacks here).
    order: list[str] = []

    class NamedCM:
        def __init__(self, name: str) -> None:
            self.name = name

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            order.append(self.name)

    # cm1 and cm2 exit themselves (right-to-left in the 'with' header).
    # ExitStack is listed last, so it exits first — firing its callbacks
    # before cm2 and cm1 get their turn.
    with NamedCM("cm1"), NamedCM("cm2"), ExitStack() as stack:
        stack.callback(order.append, "extra-b")
        stack.callback(order.append, "extra-a")

    # ExitStack callbacks fire first (LIFO within the stack),
    # then cm2, then cm1 (right-to-left across the 'with' header).
    assert order == ["extra-a", "extra-b", "cm2", "cm1"]


def test_exitstack_mixed_standalone_and_registered_cms() -> None:
    # Some CMs are managed standalone; others are delegated to ExitStack.
    # enter_context() enters the CM immediately and hands its __exit__ to the stack.
    order: list[str] = []

    class NamedCM:
        def __init__(self, name: str) -> None:
            self.name = name

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            order.append(self.name)

    # cm1 is standalone; cm2 is delegated to the stack.
    # ExitStack exits before cm1 (it appears later in the 'with' header),
    # so cm2 (registered inside the stack) and the callback exit first.
    with NamedCM("cm1"), ExitStack() as stack:
        stack.enter_context(NamedCM("cm2"))  # cm2 lifecycle owned by stack
        stack.callback(order.append, "extra")

    # Stack unwinds: extra → cm2 (LIFO), then standalone cm1 exits last.
    assert order == ["extra", "cm2", "cm1"]


def test_exitstack_pop_all_transfers_callbacks() -> None:
    # pop_all() moves all cleanups to a new ExitStack and clears the original.
    # Useful for "committing" resources — handing off ownership to a new owner.
    log: list[str] = []

    with ExitStack() as outer:
        outer.callback(log.append, "cleanup-a")
        outer.callback(log.append, "cleanup-b")

        # Transfer all cleanups to a new stack; outer is now empty
        inner = outer.pop_all()

    # outer exited without running anything (it was emptied)
    assert log == []

    # inner now owns the cleanups; closing it runs them in LIFO order
    inner.close()
    assert log == ["cleanup-b", "cleanup-a"]
