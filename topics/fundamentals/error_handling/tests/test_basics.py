# try/except/else/finally fundamentals as pytest-verified learning notes.

import pytest

# ---------------------------------------------------------------------------
# Basic try/except flow
# ---------------------------------------------------------------------------


def test_except_block_runs_when_exception_raised() -> None:
    # An exception raised inside try is caught by the matching except clause
    caught = []
    try:
        raise ValueError("oops")
    except ValueError:
        caught.append(True)
    assert caught == [True]


def test_except_block_skipped_when_no_exception() -> None:
    # The except block does not run if try completes without raising
    ran = []
    try:
        ran.append("try")
    except ValueError:
        ran.append("except")
    assert ran == ["try"]


def test_execution_continues_after_caught_exception() -> None:
    # After an exception is caught, execution continues normally after the try/except
    result = []
    try:
        raise ValueError("x")
    except ValueError:
        result.append("caught")
    result.append("after")
    assert result == ["caught", "after"]


# ---------------------------------------------------------------------------
# Catching specific exception types
# ---------------------------------------------------------------------------


def test_wrong_exception_type_propagates() -> None:
    # An except clause only catches the type(s) it specifies
    with pytest.raises(TypeError):
        try:
            raise TypeError("type error")
        except ValueError:
            pass  # TypeError is not a ValueError — the handler is skipped


def test_correct_exception_type_is_caught() -> None:
    # Matching the exact exception type stops propagation
    caught = []
    try:
        raise ValueError("v")
    except ValueError:
        caught.append(True)
    assert caught == [True]


def test_multiple_exceptions_in_tuple() -> None:
    # A tuple of exception types catches any one of them
    results = []
    for exc in (ValueError("v"), TypeError("t")):
        try:
            raise exc
        except (ValueError, TypeError) as e:
            results.append(type(e).__name__)
    assert results == ["ValueError", "TypeError"]


def test_tuple_except_does_not_catch_unrelated() -> None:
    # Exception types not in the tuple still propagate
    with pytest.raises(KeyError):
        try:
            raise KeyError("k")
        except ValueError, TypeError:
            pass


# ---------------------------------------------------------------------------
# else clause
# ---------------------------------------------------------------------------


def test_else_runs_when_no_exception() -> None:
    # The else clause runs only when the try block completes without raising
    ran = []
    try:
        ran.append("try")
    except ValueError:
        ran.append("except")
    else:
        ran.append("else")
    assert ran == ["try", "else"]


def test_else_skipped_when_exception_is_caught() -> None:
    # The else clause is skipped entirely when an exception is caught
    ran = []
    try:
        raise ValueError("x")
    except ValueError:
        ran.append("except")
    else:
        ran.append("else")  # never reached
    assert ran == ["except"]


def test_else_exception_not_caught_by_preceding_except() -> None:
    # An exception raised inside else is NOT caught by the preceding except clauses
    # else runs after try succeeds, so its exceptions propagate to the caller
    with pytest.raises(RuntimeError):
        try:
            pass  # no exception in try
        except ValueError:
            pass
        else:
            raise RuntimeError("from else")  # propagates — no matching handler here


# ---------------------------------------------------------------------------
# finally clause
# ---------------------------------------------------------------------------


def test_finally_runs_when_no_exception() -> None:
    # finally always executes — even when there is no exception
    ran = []
    try:
        ran.append("try")
    finally:
        ran.append("finally")
    assert ran == ["try", "finally"]


def test_finally_runs_when_exception_is_caught() -> None:
    # finally runs after the except handler completes
    ran = []
    try:
        raise ValueError("x")
    except ValueError:
        ran.append("except")
    finally:
        ran.append("finally")
    assert ran == ["except", "finally"]


def test_finally_runs_even_when_exception_propagates() -> None:
    # finally runs even when no except clause catches the exception
    ran = []
    with pytest.raises(ValueError):
        try:
            raise ValueError("x")
        finally:
            ran.append("finally")  # runs before the exception propagates out
    assert ran == ["finally"]


def test_finally_runs_even_with_early_return() -> None:
    # finally runs even when the try block returns early
    ran: list[str] = []

    def f() -> str:
        try:
            return "try"
        finally:
            ran.append("finally")

    result = f()
    assert result == "try"
    assert ran == ["finally"]


def test_pep765_return_in_finally_is_syntax_warning() -> None:
    # Python 3.14 (PEP 765): return inside a finally block emits a SyntaxWarning
    # Previously this silently swallowed exceptions and return values — now Python warns
    code = "def f():\n    try:\n        pass\n    finally:\n        return 1\n"
    with pytest.warns(SyntaxWarning, match="finally"):
        compile(code, "<string>", "exec")


def test_pep765_break_in_finally_is_syntax_warning() -> None:
    # break inside a finally block also triggers a SyntaxWarning in Python 3.14
    code = (
        "def f():\n"
        "    for i in range(3):\n"
        "        try:\n"
        "            pass\n"
        "        finally:\n"
        "            break\n"
    )
    with pytest.warns(SyntaxWarning, match="finally"):
        compile(code, "<string>", "exec")


# ---------------------------------------------------------------------------
# Exception variable scope
# ---------------------------------------------------------------------------


def test_exception_variable_accessible_inside_except() -> None:
    # The 'as e' variable is accessible throughout the except block
    try:
        raise ValueError("hello")
    except ValueError as e:
        assert str(e) == "hello"  # noqa: PT017 — intentional: demonstrating 'as e' access pattern
        assert isinstance(e, ValueError)  # noqa: PT017


def test_exception_variable_deleted_after_except_block() -> None:
    # Python 3: the 'as e' binding is explicitly deleted when the except block exits
    # This prevents a reference cycle: e -> e.__traceback__ -> frame -> e
    try:
        raise ValueError("test")
    except ValueError as e:
        saved = e  # save the object before the binding disappears

    # 'e' no longer exists in this scope — Python deleted it
    assert "e" not in locals()
    # But the object we saved is still alive
    assert str(saved) == "test"


def test_saved_reference_survives_scope_deletion() -> None:
    # Python deletes the name 'e', not the exception object itself
    # Assigning to another name inside the block keeps the object alive
    ref = None
    try:
        raise RuntimeError("keep me")
    except RuntimeError as e:
        ref = e
    assert isinstance(ref, RuntimeError)
    assert str(ref) == "keep me"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class _AppError(Exception):
    pass


class _DBError(_AppError):
    pass


def test_catching_base_class_catches_subclass() -> None:
    # A parent class in the except clause catches instances of all its subclasses
    caught_type = None
    try:
        raise _DBError("db failed")
    except _AppError as e:
        caught_type = type(e)
    # The handler matched, but the actual type is still _DBError
    assert caught_type is _DBError


def test_except_exception_does_not_catch_system_exit() -> None:
    # SystemExit is a BaseException, not an Exception — 'except Exception' misses it
    with pytest.raises(SystemExit):
        try:
            raise SystemExit(0)
        except Exception:
            pass  # not reached — SystemExit bypasses this handler


def test_bare_except_catches_system_exit() -> None:
    # Bare 'except:' is equivalent to 'except BaseException:' and catches everything,
    # including SystemExit and KeyboardInterrupt — this is an antipattern
    caught = []
    try:
        raise SystemExit(0)
    except:  # noqa: E722 — intentional bare except to demonstrate the antipattern
        caught.append(True)
    assert caught == [True]


def test_exception_hierarchy_issubclass() -> None:
    # SystemExit and KeyboardInterrupt descend from BaseException, not Exception
    assert issubclass(Exception, BaseException)
    assert issubclass(ValueError, Exception)
    assert issubclass(SystemExit, BaseException)
    assert not issubclass(SystemExit, Exception)
    assert issubclass(KeyboardInterrupt, BaseException)
    assert not issubclass(KeyboardInterrupt, Exception)
