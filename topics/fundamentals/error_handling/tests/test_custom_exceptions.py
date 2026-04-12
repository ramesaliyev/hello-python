# Custom exception classes as pytest-verified learning notes.

import pytest

# ---------------------------------------------------------------------------
# Module-level exception hierarchy used across multiple tests
# ---------------------------------------------------------------------------


class AppError(Exception):
    pass


class NetworkError(AppError):
    pass


class DatabaseError(AppError):
    pass


class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


# ---------------------------------------------------------------------------
# Basic custom exceptions
# ---------------------------------------------------------------------------


def test_custom_exception_can_be_raised_and_caught() -> None:
    # A custom exception class behaves like any built-in exception
    with pytest.raises(AppError):
        raise AppError("something failed")


def test_custom_exception_is_exception_subclass() -> None:
    # Custom exceptions derived from Exception integrate with all standard handlers
    assert issubclass(AppError, Exception)
    assert issubclass(AppError, BaseException)


def test_custom_exception_message_in_args() -> None:
    # The message passed to the constructor is stored in .args
    with pytest.raises(AppError) as exc_info:
        raise AppError("test message")
    assert exc_info.value.args[0] == "test message"


def test_deriving_from_base_exception_bypasses_except_exception() -> None:
    # Custom exceptions should inherit from Exception, not BaseException directly
    # Inheriting from BaseException makes the exception invisible to 'except Exception'
    class BadError(BaseException):
        pass

    with pytest.raises(BadError):
        try:
            raise BadError("missed")
        except Exception:
            pass  # not reached — BadError is a BaseException, not an Exception


# ---------------------------------------------------------------------------
# Custom attributes
# ---------------------------------------------------------------------------


def test_custom_exception_exposes_field_attribute() -> None:
    # Extra attributes on custom exceptions give callers structured error context
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("email", "invalid format")
    assert exc_info.value.field == "email"
    assert exc_info.value.message == "invalid format"


def test_custom_exception_str_uses_super_init_message() -> None:
    # Calling super().__init__("...") sets args and thus str()
    exc = ValidationError("age", "must be positive")
    assert str(exc) == "age: must be positive"


def test_custom_exception_args_reflect_super_init() -> None:
    # super().__init__ was called with one formatted string, so args has one element
    exc = ValidationError("age", "must be positive")
    assert exc.args == ("age: must be positive",)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


def test_catching_parent_catches_child_type() -> None:
    # Catching a parent class catches all its subclasses; the actual type is preserved
    caught_type = None
    try:
        raise NetworkError("timeout")
    except AppError as e:
        caught_type = type(e)
    assert caught_type is NetworkError


def test_specific_handler_takes_priority_over_general() -> None:
    # Python tries except clauses top-to-bottom and stops at the first match
    handler = None
    try:
        raise NetworkError("conn refused")
    except NetworkError:
        handler = "specific"
    except AppError:
        handler = "general"
    assert handler == "specific"


def test_hierarchy_allows_broad_catch_at_top_level() -> None:
    # Catching the base class handles all specialised errors uniformly
    caught = []
    for exc in [NetworkError("net"), DatabaseError("db"), AppError("app")]:
        try:
            raise exc
        except AppError:
            caught.append(type(exc).__name__)
    assert caught == ["NetworkError", "DatabaseError", "AppError"]


# ---------------------------------------------------------------------------
# add_note() — Python 3.11+
# ---------------------------------------------------------------------------


def test_add_note_appends_to_notes_list() -> None:
    # add_note() attaches a free-form string to the exception
    e = ValueError("base error")
    e.add_note("See the docs at /help")
    assert e.__notes__ == ["See the docs at /help"]


def test_add_note_preserves_insertion_order() -> None:
    # Multiple notes are stored in the order they were added
    e = ValueError("base")
    e.add_note("first context")
    e.add_note("second context")
    assert e.__notes__ == ["first context", "second context"]


def test_add_note_does_not_change_args_or_str() -> None:
    # Notes are separate from args — they appear in tracebacks but not in str(exc)
    e = ValueError("original message")
    e.add_note("extra context")
    assert e.args == ("original message",)
    assert str(e) == "original message"


def test_fresh_exception_has_no_notes_attribute() -> None:
    # __notes__ is only created on the first add_note() call — absent by default
    assert not hasattr(ValueError("x"), "__notes__")


def test_add_note_to_caught_exception_before_reraise() -> None:
    # The practical pattern: enrich an exception as it propagates up the call stack
    with pytest.raises(ValueError) as exc_info:
        try:
            raise ValueError("low-level failure")
        except ValueError as e:
            e.add_note("while processing request id=42")
            raise  # bare raise preserves the enriched exception

    assert exc_info.value.__notes__ == ["while processing request id=42"]


# ---------------------------------------------------------------------------
# args and str() edge cases
# ---------------------------------------------------------------------------


def test_exception_with_no_args() -> None:
    # An exception raised with no arguments has empty args and empty str
    exc = ValueError()
    assert exc.args == ()
    assert str(exc) == ""


def test_exception_str_unwraps_single_arg() -> None:
    # Single-arg exceptions show the arg directly, without tuple notation
    assert str(ValueError("msg")) == "msg"


def test_exception_str_shows_tuple_for_multiple_args() -> None:
    # Multiple args are shown as their tuple repr
    assert str(ValueError("a", "b")) == "('a', 'b')"
