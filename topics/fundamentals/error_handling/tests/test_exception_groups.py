# ExceptionGroup and except* syntax (PEP 654, Python 3.11+) as learning notes.
# ruff: noqa: PT017 — assertions inside except*/except blocks are intentional here

# ---------------------------------------------------------------------------
# Why ExceptionGroup exists
# ---------------------------------------------------------------------------
#
# Traditional exception handling is *serial*: a single exception propagates up
# the call stack and the first matching `except` clause wins. That model breaks
# down as soon as multiple things can fail *at the same time*:
#
#   - asyncio.TaskGroup (Python 3.11+) runs several coroutines concurrently.
#     If two of them raise, you cannot propagate both through a single `raise`.
#   - concurrent.futures / multiprocessing: a batch of workers may all fail.
#   - Bulk validation: you want to report every invalid field, not just the first.
#   - Test runners, build systems, import machinery: collect all failures, then
#     surface them together.
#
# ExceptionGroup solves this by treating a *set of exceptions* as a first-class
# value.  You can raise it, catch it, inspect it, and split it — without losing
# any of the individual errors.
#
# ---------------------------------------------------------------------------
# Where you'll encounter it
# ---------------------------------------------------------------------------
#
#   async with asyncio.TaskGroup() as tg:   # stdlib, Python 3.11+
#       tg.create_task(fetch(url1))
#       tg.create_task(fetch(url2))
#   # If both tasks raise, Python raises an ExceptionGroup with both errors.
#   # except* lets you handle each error type independently in one try block.
#
# The `except*` counterpart is equally important: unlike `except` (which stops
# at the first matching clause), every `except*` handler that matches runs,
# each receiving its own sub-group.  Unmatched exceptions are automatically
# re-raised so nothing is silently swallowed.
#
# ---------------------------------------------------------------------------

import pytest

# ---------------------------------------------------------------------------
# ExceptionGroup basics
# ---------------------------------------------------------------------------


def test_exception_group_creation() -> None:
    # ExceptionGroup wraps multiple unrelated exceptions under a single label
    eg = ExceptionGroup("label", [ValueError("v"), TypeError("t")])
    assert eg.message == "label"
    assert len(eg.exceptions) == 2


def test_exception_group_message_attribute() -> None:
    # .message is the human-readable label (first constructor argument)
    eg = ExceptionGroup("my group", [ValueError()])
    assert eg.message == "my group"


def test_exception_group_exceptions_is_a_tuple() -> None:
    # .exceptions is an immutable tuple of the contained exceptions
    eg = ExceptionGroup("g", [ValueError("a"), TypeError("b")])
    assert isinstance(eg.exceptions, tuple)
    assert isinstance(eg.exceptions[0], ValueError)
    assert isinstance(eg.exceptions[1], TypeError)


def test_exception_group_is_an_exception() -> None:
    # ExceptionGroup inherits from Exception — 'except Exception' can catch it
    eg = ExceptionGroup("g", [ValueError()])
    assert isinstance(eg, Exception)
    assert isinstance(eg, BaseException)


def test_exception_group_rejects_base_exceptions() -> None:
    # ExceptionGroup can only contain Exception subclasses, not raw BaseExceptions
    # Use BaseExceptionGroup for SystemExit, KeyboardInterrupt, etc.
    with pytest.raises(TypeError):
        ExceptionGroup("g", [SystemExit(0)])  # type: ignore[type-var]  # noqa: PLW0133


# ---------------------------------------------------------------------------
# except* syntax
# ---------------------------------------------------------------------------


def test_except_star_catches_matching_exceptions_from_group() -> None:
    # except* filters the group and handles only the matching exception types
    caught: list[BaseException] = []
    try:
        raise ExceptionGroup("eg", [ValueError("v"), TypeError("t")])
    except* ValueError as eg:
        caught.extend(eg.exceptions)
    except* TypeError:
        pass

    assert len(caught) == 1
    assert isinstance(caught[0], ValueError)


def test_except_star_handler_receives_an_exception_group() -> None:
    # The variable bound by 'except* E as eg' is itself an ExceptionGroup,
    # not the individual exception — it contains only the matching ones.
    # To act on each error individually, iterate over eg.exceptions.
    messages: list[str] = []
    try:
        raise ExceptionGroup("g", [ValueError("a"), ValueError("b")])
    except* ValueError as eg:
        assert isinstance(eg, ExceptionGroup)
        assert len(eg.exceptions) == 2
        for exc in eg.exceptions:
            messages.append(str(exc))  # noqa: PERF401 -- loop is intentional to demo

    assert messages == ["a", "b"]


def test_multiple_except_star_handlers_all_fire() -> None:
    # Unlike regular except (stops at first match), ALL matching except* handlers run
    # This is the key semantic difference: each handler processes its slice of the group
    fired: list[str] = []
    try:
        raise ExceptionGroup(
            "mixed",
            [ValueError("v"), TypeError("t"), KeyError("k")],
        )
    except* ValueError:
        fired.append("ValueError")
    except* TypeError:
        fired.append("TypeError")
    except* KeyError:
        fired.append("KeyError")

    assert fired == ["ValueError", "TypeError", "KeyError"]


def test_unmatched_exceptions_propagate_as_new_group() -> None:
    # Exceptions in the group that no except* clause handles are re-raised
    # as a new ExceptionGroup after all handlers have run
    with pytest.raises(ExceptionGroup) as exc_info:
        try:
            raise ExceptionGroup("mixed", [ValueError("handled"), KeyError("missed")])
        except* ValueError:
            pass  # ValueError is handled; KeyError is not

    remaining = exc_info.value
    assert len(remaining.exceptions) == 1
    assert isinstance(remaining.exceptions[0], KeyError)


def test_except_star_with_tuple_of_types() -> None:
    # Like regular except, except* accepts a tuple of types in one handler
    caught: list[BaseException] = []
    try:
        raise ExceptionGroup("g", [ValueError("v"), TypeError("t")])
    except* (ValueError, TypeError) as eg:
        caught.extend(eg.exceptions)

    assert len(caught) == 2


# ---------------------------------------------------------------------------
# BaseExceptionGroup
# ---------------------------------------------------------------------------


def test_base_exception_group_wraps_base_exceptions() -> None:
    # BaseExceptionGroup can contain BaseException subclasses like SystemExit
    beg = BaseExceptionGroup("beg", [SystemExit(0), KeyboardInterrupt()])
    assert isinstance(beg, BaseExceptionGroup)
    assert len(beg.exceptions) == 2


def test_base_exception_group_is_not_exception() -> None:
    # BaseExceptionGroup is only a BaseException — 'except Exception' won't catch it
    assert issubclass(BaseExceptionGroup, BaseException)
    assert not issubclass(BaseExceptionGroup, Exception)


def test_exception_group_is_both_base_exception_group_and_exception() -> None:
    # ExceptionGroup inherits from both BaseExceptionGroup and Exception
    assert issubclass(ExceptionGroup, BaseExceptionGroup)
    assert issubclass(ExceptionGroup, Exception)


# ---------------------------------------------------------------------------
# subgroup() and split()
# ---------------------------------------------------------------------------


def test_subgroup_returns_matching_exceptions() -> None:
    # subgroup() returns a new ExceptionGroup with only the matching exceptions
    eg = ExceptionGroup("mixed", [ValueError("a"), TypeError("b"), ValueError("c")])
    sub = eg.subgroup(ValueError)
    assert sub is not None
    assert len(sub.exceptions) == 2
    assert all(isinstance(e, ValueError) for e in sub.exceptions)


def test_subgroup_returns_none_when_no_match() -> None:
    # subgroup() returns None if no exceptions match the condition
    eg = ExceptionGroup("mixed", [ValueError("v"), TypeError("t")])
    assert eg.subgroup(KeyError) is None


def test_subgroup_accepts_a_callable() -> None:
    # subgroup() also accepts a predicate for fine-grained filtering
    eg = ExceptionGroup(
        "vals",
        [ValueError("keep this"), ValueError("discard"), TypeError("t")],
    )
    sub = eg.subgroup(lambda e: isinstance(e, ValueError) and "keep" in str(e))
    assert sub is not None
    assert len(sub.exceptions) == 1
    assert str(sub.exceptions[0]) == "keep this"


def test_split_returns_match_and_rest() -> None:
    # split() partitions the group into (matching, non-matching)
    eg = ExceptionGroup("mixed", [ValueError("v"), TypeError("t")])
    match, rest = eg.split(ValueError)
    assert match is not None
    assert rest is not None
    assert len(match.exceptions) == 1
    assert isinstance(match.exceptions[0], ValueError)
    assert len(rest.exceptions) == 1
    assert isinstance(rest.exceptions[0], TypeError)


def test_split_match_is_none_when_nothing_matches() -> None:
    # If nothing matches, the first element of the tuple is None
    eg = ExceptionGroup("vals", [ValueError("v")])
    match, rest = eg.split(KeyError)
    assert match is None
    assert rest is not None


def test_split_rest_is_none_when_everything_matches() -> None:
    # If everything matches, the second element of the tuple is None
    eg = ExceptionGroup("vals", [ValueError("a"), ValueError("b")])
    match, rest = eg.split(ValueError)
    assert match is not None
    assert rest is None
    assert len(match.exceptions) == 2


# ---------------------------------------------------------------------------
# Nested ExceptionGroups
# ---------------------------------------------------------------------------


def test_nested_exception_group_creation() -> None:
    # ExceptionGroups can be nested — useful when aggregating groups of groups
    inner = ExceptionGroup("inner", [ValueError("deep")])
    outer = ExceptionGroup("outer", [inner, TypeError("shallow")])
    assert len(outer.exceptions) == 2
    assert isinstance(outer.exceptions[0], ExceptionGroup)


def test_except_star_matches_exceptions_at_any_nesting_depth() -> None:
    # except* recursively searches nested ExceptionGroups for matching exceptions
    # The result group preserves the original nesting structure — it is not flattened
    try:
        inner = ExceptionGroup("inner", [ValueError("deep")])
        raise ExceptionGroup("outer", [inner, TypeError("shallow")])
    except* ValueError as eg:
        # eg contains the matched inner ExceptionGroup with its structure intact
        assert isinstance(eg.exceptions[0], ExceptionGroup)
        # The actual ValueError lives one level down inside the preserved inner group
        assert isinstance(eg.exceptions[0].exceptions[0], ValueError)
    except* TypeError as eg:
        assert isinstance(eg.exceptions[0], TypeError)
