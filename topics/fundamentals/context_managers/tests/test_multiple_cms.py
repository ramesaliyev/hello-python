# Multiple context managers in one with statement as pytest-verified learning notes.

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
# Multiple context managers
# ---------------------------------------------------------------------------


def test_multiple_cms_stacked_in_one_with_statement() -> None:
    # 'with A() as a, B() as b' is shorthand for nesting two with blocks
    cm1, cm2 = TrackedCM("first"), TrackedCM("second")
    with cm1 as a, cm2 as b:
        assert a is cm1
        assert b is cm2


def test_multiple_cms_enter_left_to_right_exit_right_to_left() -> None:
    # Enter order: left-to-right. Exit order: right-to-left (LIFO).
    order: list[str] = []

    class OrderedCM:
        def __init__(self, name: str) -> None:
            self.name = name

        def __enter__(self) -> Self:
            order.append(f"enter:{self.name}")
            return self

        def __exit__(self, *args: object) -> None:
            order.append(f"exit:{self.name}")

    with OrderedCM("a"), OrderedCM("b"):
        pass

    assert order == ["enter:a", "enter:b", "exit:b", "exit:a"]


def test_all_cms_exited_even_on_exception() -> None:
    # All context managers in a with statement are exited even if the body raises
    cm1, cm2 = TrackedCM("first"), TrackedCM("second")
    with pytest.raises(RuntimeError), cm1, cm2:
        raise RuntimeError("boom")
    assert cm1.exited is True
    assert cm2.exited is True


def test_second_cm_exception_does_not_prevent_first_cm_exit() -> None:
    # Even when an inner CM's exit raises, the outer CM still gets its __exit__ called.
    # The outer CM sees the exception raised by the inner CM's __exit__.
    outer_exited = False

    class OuterCM:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            nonlocal outer_exited
            outer_exited = True

    class InnerCM:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            raise RuntimeError("inner exit failed")

    with pytest.raises(RuntimeError, match="inner exit failed"), OuterCM(), InnerCM():
        pass

    assert outer_exited is True
