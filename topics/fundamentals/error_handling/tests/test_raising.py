# Raising and chaining exceptions as pytest-verified learning notes.

import traceback as tb_module

import pytest

# ---------------------------------------------------------------------------
# Basic raising
# ---------------------------------------------------------------------------


def test_raise_with_type_auto_instantiates() -> None:
    # Raising a class (not an instance) auto-instantiates it with no arguments
    with pytest.raises(ValueError):
        raise ValueError


def test_raise_with_instance_carries_message() -> None:
    # Raising an instance preserves the message in args
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("something went wrong")
    assert exc_info.value.args[0] == "something went wrong"


def test_pytest_raises_match_checks_message() -> None:
    # pytest.raises(match=...) asserts the string representation matches a regex
    with pytest.raises(ValueError, match="invalid value"):
        raise ValueError("invalid value for field 'x'")


# ---------------------------------------------------------------------------
# Re-raising
# ---------------------------------------------------------------------------


def test_bare_raise_preserves_traceback() -> None:
    # Bare 'raise' inside an except block re-raises without modifying the traceback
    # The traceback still points to the original raise site
    def inner() -> None:
        raise ValueError("original")

    def wrapper_bare() -> None:
        try:
            inner()
        except ValueError:  # noqa: TRY203 — intentional: demonstrating bare raise traceback
            raise  # bare raise — traceback unchanged

    with pytest.raises(ValueError) as exc_info:
        wrapper_bare()

    frames = tb_module.extract_tb(exc_info.value.__traceback__)
    # The innermost frame is still 'inner', where the exception originated
    assert frames[-1].name == "inner"


def test_raise_e_adds_extra_traceback_frame() -> None:
    # 'raise e' adds an extra frame at the re-raise site; bare raise does not
    # This makes tracebacks longer and the actual origin less obvious
    def inner() -> None:
        raise ValueError("original")

    def wrapper_bare() -> None:
        try:
            inner()
        except ValueError:  # noqa: TRY203 — intentional: demonstrating bare raise traceback
            raise

    def wrapper_raise_e() -> None:
        try:
            inner()
        except ValueError as e:  # noqa: TRY203 — intentional: demonstrating raise-e antipattern
            raise e  # noqa: TRY201 — intentional antipattern: raise e adds an extra frame

    with pytest.raises(ValueError) as exc_bare:
        wrapper_bare()
    with pytest.raises(ValueError) as exc_raise_e:
        wrapper_raise_e()

    frames_bare = tb_module.extract_tb(exc_bare.value.__traceback__)
    frames_raise_e = tb_module.extract_tb(exc_raise_e.value.__traceback__)

    # Both ultimately point back to inner() as the origin
    assert frames_bare[-1].name == "inner"
    assert frames_raise_e[-1].name == "inner"
    # But raise e inserts an extra frame for the re-raise call site itself
    assert len(frames_raise_e) > len(frames_bare)
    assert frames_raise_e[-2].name == "wrapper_raise_e"  # the extra noise frame


# ---------------------------------------------------------------------------
# Explicit exception chaining (raise ... from ...)
# ---------------------------------------------------------------------------


def test_raise_from_sets_cause() -> None:
    # 'raise B() from A()' explicitly chains: B.__cause__ = A
    original = ValueError("original")
    with pytest.raises(RuntimeError) as exc_info:
        try:
            raise original
        except ValueError as e:
            raise RuntimeError("new problem") from e
    assert exc_info.value.__cause__ is original


def test_raise_from_sets_suppress_context() -> None:
    # Explicit chaining sets __suppress_context__ = True, hiding the implicit chain
    # Tracebacks show "The above exception was the direct cause of..."
    with pytest.raises(RuntimeError) as exc_info:
        try:
            raise ValueError("original")
        except ValueError as e:
            raise RuntimeError("wrapped") from e
    assert exc_info.value.__suppress_context__ is True


def test_raise_from_none_suppresses_context() -> None:
    # 'raise B() from None' signals "this is a clean new error, ignore the cause"
    # __context__ still records the original, but __suppress_context__ hides it
    with pytest.raises(RuntimeError) as exc_info:
        try:
            raise ValueError("internal detail")
        except ValueError:
            raise RuntimeError("user-facing error") from None

    exc = exc_info.value
    assert exc.__cause__ is None
    assert isinstance(exc.__context__, ValueError)  # original is still recorded...
    assert exc.__suppress_context__ is True  # ...but hidden from the traceback


# ---------------------------------------------------------------------------
# Implicit exception chaining
# ---------------------------------------------------------------------------


def test_raising_inside_except_sets_context() -> None:
    # Raising a new exception inside an except block implicitly chains them
    # The original exception is stored in __context__
    original = ValueError("first")
    with pytest.raises(RuntimeError) as exc_info:
        try:
            raise original
        except ValueError:
            raise RuntimeError("second")  # noqa: B904 — intentional: demonstrating implicit chaining

    exc = exc_info.value
    assert exc.__context__ is original
    assert exc.__cause__ is None  # not an explicit chain
    assert exc.__suppress_context__ is False  # traceback shows "during handling of..."


def test_context_and_cause_are_distinct() -> None:
    # __context__: set implicitly whenever raising inside an except block
    # __cause__:   set only with 'raise ... from ...'
    # __suppress_context__: True hides __context__ from the traceback display
    with pytest.raises(RuntimeError) as exc_info:
        try:
            raise ValueError("cause")
        except ValueError as e:
            raise RuntimeError("effect") from e

    exc = exc_info.value
    assert exc.__cause__ is not None  # set by 'from'
    assert exc.__context__ is not None  # also set, because raised inside except
    assert exc.__suppress_context__ is True  # 'from' sets this True, hiding __context__


# ---------------------------------------------------------------------------
# What __suppress_context__ controls in formatted tracebacks
# ---------------------------------------------------------------------------
#
# __suppress_context__ tells the traceback formatter what to print:
#
#   (Below in order: implicit, explicit, and explicit with no cause.)
#
#   raise B inside except  → False → "During handling of the above exception..."
#   raise B from A         → True  → "The above exception was the direct cause..."
#   raise B from None      → True  → (nothing — original exception hidden entirely)


def test_suppress_context_false_shows_during_handling_message() -> None:
    # Implicit chaining
    # When __suppress_context__ is False (implicit chain), the formatted traceback
    # includes "During handling of the above exception, another exception occurred"
    try:
        try:
            raise ValueError("first")
        except ValueError:
            raise RuntimeError("second")  # noqa: B904 — intentional: implicit chain
    except RuntimeError as exc:
        lines = "".join(tb_module.format_exception(exc))
    assert "During handling of the above exception" in lines


def test_suppress_context_true_shows_direct_cause_message() -> None:
    # Explicit chaining
    # When __suppress_context__ is True (raise ... from ...), the formatted traceback
    # prints "The above exception was the direct cause of the following exception"
    try:
        try:
            raise ValueError("first")
        except ValueError as e:
            raise RuntimeError("second") from e
    except RuntimeError as exc:
        lines = "".join(tb_module.format_exception(exc))
    assert "direct cause of the following exception" in lines
    assert "During handling of" not in lines


def test_suppress_context_true_with_no_cause_hides_context_entirely() -> None:
    # Explicit chaining with no cause
    # raise B from None sets __suppress_context__ = True and __cause__ = None
    # The formatted traceback shows only B — the original exception is not printed
    try:
        try:
            raise ValueError("internal detail")
        except ValueError:
            raise RuntimeError("user-facing error") from None
    except RuntimeError as exc:
        lines = "".join(tb_module.format_exception(exc))
    assert "internal detail" not in lines
    assert "During handling of" not in lines
    assert "direct cause" not in lines


def test_manually_setting_suppress_context_hides_implicit_chain() -> None:
    # __suppress_context__ is just a regular bool — setting it manually suppresses the
    # "During handling of..." message even for an implicitly-chained exception.
    # This is how libraries can hide noisy internal causes from user-facing errors.
    try:
        try:
            raise ValueError("internal")
        except ValueError:
            exc = RuntimeError("external")
            exc.__suppress_context__ = True
            raise exc  # noqa: B904 — intentional: demonstrating manual __suppress_context__
    except RuntimeError as caught:
        lines = "".join(tb_module.format_exception(caught))
    assert "During handling of" not in lines
    assert "internal" not in lines


# ---------------------------------------------------------------------------
# Exception attributes
# ---------------------------------------------------------------------------


def test_traceback_attribute_is_set() -> None:
    # Every caught exception has a __traceback__ pointing into the call stack
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("x")
    assert exc_info.value.__traceback__ is not None
    assert isinstance(exc_info.value.__traceback__.tb_lineno, int)


def test_args_is_a_tuple_of_constructor_arguments() -> None:
    # Exception stores all constructor arguments in the .args tuple
    exc = ValueError("a", "b", "c")
    assert exc.args == ("a", "b", "c")


def test_str_of_single_arg_is_unwrapped() -> None:
    # str() of a single-arg exception returns the arg directly, without tuple notation
    assert str(ValueError("msg")) == "msg"


def test_str_of_multiple_args_shows_tuple() -> None:
    # str() of an exception with multiple args shows them as a tuple repr
    assert str(ValueError("a", "b")) == "('a', 'b')"


def test_str_of_no_args_is_empty_string() -> None:
    # An exception raised with no arguments has an empty string representation
    assert str(ValueError()) == ""
    assert ValueError().args == ()
