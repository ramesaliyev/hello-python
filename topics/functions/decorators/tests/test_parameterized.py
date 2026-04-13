# Parameterized decorators: factory pattern, optional arguments, and common mistakes.

import functools

import pytest

# ---------------------------------------------------------------------------
# 1. Three-layer structure — factory → decorator → wrapper
#
# The factory pattern is the standard, explicit approach. Always requires
# parentheses at the call site: @repeat(3) — never bare @repeat.
#
# Prefer this when:
#   • arguments are required (no sensible default exists)
#   • clarity matters more than call-site convenience
#   • you want the simplest possible implementation to read and maintain
# ---------------------------------------------------------------------------


def test_parameterized_decorator_uses_three_nested_layers() -> None:
    # A plain decorator:         func = decorator(func)
    # A parameterized decorator: func = factory(arg)(func)
    #
    #   factory(arg)      ← takes configuration, returns a decorator
    #     decorator(func) ← takes the function, returns a wrapper
    #       wrapper(...)  ← the actual replacement called at runtime
    def repeat(times: int):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> None:
                for _ in range(times):
                    func(*args, **kwargs)

            return wrapper

        return decorator

    results: list[str] = []

    @repeat(times=3)
    def say(msg: str) -> None:
        results.append(msg)

    say("hi")
    assert results == ["hi", "hi", "hi"]


def test_parameterized_decorator_desugars_to_two_sequential_calls() -> None:
    # @repeat(3)
    # def func(): ...
    # is exactly:  func = repeat(3)(func)
    definition_log: list[str] = []

    def repeat(times: int):
        definition_log.append(f"factory(times={times})")

        def decorator(func):
            definition_log.append(f"decorator({func.__name__})")

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> None:
                for _ in range(times):
                    func(*args, **kwargs)

            return wrapper

        return decorator

    @repeat(2)
    def greet() -> None:
        pass

    # Both calls happen at definition time, before greet() is ever called
    assert definition_log == ["factory(times=2)", "decorator(greet)"]


# ---------------------------------------------------------------------------
# 2. Practical examples
# ---------------------------------------------------------------------------


def test_retry_decorator_with_configurable_attempts_and_exception_type() -> None:
    def retry(times: int, exception: type[Exception] = Exception):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exc: Exception | None = None
                for _ in range(times):
                    try:
                        return func(*args, **kwargs)
                    except exception as exc:
                        last_exc = exc
                raise RuntimeError(f"Failed after {times} attempts") from last_exc

            return wrapper

        return decorator

    attempt = {"n": 0}

    @retry(times=3, exception=ValueError)
    def flaky() -> str:
        attempt["n"] += 1
        if attempt["n"] < 3:
            raise ValueError("not ready")
        return "ok"

    assert flaky() == "ok"
    assert attempt["n"] == 3


def test_prefix_result_decorator_with_configurable_text() -> None:
    def prefix_result(prefix: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> str:
                return prefix + str(func(*args, **kwargs))

            return wrapper

        return decorator

    @prefix_result("ERROR: ")
    def get_message() -> str:
        return "disk full"

    assert get_message() == "ERROR: disk full"


def test_clamp_decorator_restricts_numeric_return_value_to_a_range() -> None:
    def clamp(low: float, high: float):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> float:
                return max(low, min(high, func(*args, **kwargs)))

            return wrapper

        return decorator

    @clamp(0.0, 1.0)
    def noisy_sensor() -> float:
        return 1.8  # raw value is out of range

    assert noisy_sensor() == 1.0


def test_require_role_decorator_guards_access_by_user_role() -> None:
    def require_role(role: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(user_role: str, *args, **kwargs):
                if user_role != role:
                    raise PermissionError(f"requires {role!r}, got {user_role!r}")
                return func(user_role, *args, **kwargs)

            return wrapper

        return decorator

    @require_role("admin")
    def delete_all(user_role: str) -> str:
        return f"deleted by {user_role}"

    assert delete_all("admin") == "deleted by admin"

    with pytest.raises(PermissionError, match="requires 'admin'"):
        delete_all("guest")


# ---------------------------------------------------------------------------
# 3. Optional-argument decorator — works as @deco or @deco(arg)
#
# The optional-argument pattern lets one function serve both call styles:
#   @log_result              ← bare, uses defaults
#   @log_result()            ← empty parens, still uses defaults
#   @log_result(label="x")   ← with arguments
#
# Mechanism: declare `func=None` as the first positional parameter.
# • When used bare (@log_result), Python passes the decorated function as
#   `func`, so the decorator builds the wrapper immediately.
# • When called with parens (@log_result() or @log_result(label="x")),
#   `func` stays None, so the decorator returns a partially-applied version
#   of itself (via functools.partial) to act as the real decorator.
#
# Factory pattern vs. optional-argument pattern — when to use which:
#
#   Factory (sections 1-2)          Optional-argument (this section)
#   ──────────────────────────────   ────────────────────────────────
#   Always needs @deco(args)         Works as @deco or @deco(args)
#   Arguments are required           Arguments are optional / have defaults
#   Implementation is simpler        Implementation has the func=None trick
#   Preferred in modern code         Use only when bare @deco is genuinely
#                                    useful and avoids boilerplate for callers
#
# Modern recommendation: default to the factory pattern for clarity.
# Add optional-argument support only when the decorator is commonly used
# without arguments and the convenience is worth the added complexity.
# ---------------------------------------------------------------------------


def test_optional_arg_decorator_works_without_parentheses() -> None:
    # A single decorator usable two ways:
    #   @log_result           — no parens, default label
    #   @log_result(label=…)  — with parens, custom label
    log: list[str] = []

    def log_result(func=None, *, label: str = "result"):
        if func is None:
            # Called as @log_result() or @log_result(label="x"):
            # Python passed no positional arg, so return a proper decorator.
            return functools.partial(log_result, label=label)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            log.append(f"{label}={value}")
            return value

        return wrapper

    @log_result
    def double(n: int) -> int:
        return n * 2

    double(5)
    assert log == ["result=10"]


def test_optional_arg_decorator_works_with_parentheses_and_custom_label() -> None:
    log: list[str] = []

    def log_result(func=None, *, label: str = "result"):
        if func is None:
            return functools.partial(log_result, label=label)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            log.append(f"{label}={value}")
            return value

        return wrapper

    @log_result(label="answer")
    def double(n: int) -> int:
        return n * 2

    double(5)
    assert log == ["answer=10"]


def test_optional_arg_decorator_works_with_empty_parentheses() -> None:
    log: list[str] = []

    def log_result(func=None, *, label: str = "result"):
        if func is None:
            return functools.partial(log_result, label=label)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            log.append(f"{label}={value}")
            return value

        return wrapper

    @log_result()  # empty parens — uses default label
    def double(n: int) -> int:
        return n * 2

    double(5)
    assert log == ["result=10"]


# ---------------------------------------------------------------------------
# 4. Gotcha: forgetting to call the factory
# ---------------------------------------------------------------------------


def test_gotcha_omitting_factory_parens_passes_the_function_as_the_config_arg() -> None:
    # @repeat(3)  ← correct: repeat is called first, returns the real decorator
    # @repeat     ← wrong:  repeat receives the function as its `times` argument
    def repeat(times: int):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> None:
                for _ in range(times):  # TypeError: times is a function, not an int
                    func(*args, **kwargs)

            return wrapper

        return decorator

    @repeat  # type: ignore[arg-type]  # intentional mistake to show the gotcha
    def greet() -> None:
        pass

    # `greet` is now `decorator` (waiting for a `func` arg), not a zero-arg callable.
    # The mistake is invisible at decoration time — only surfaces when called.
    with pytest.raises(TypeError):
        greet()  # TypeError: decorator() missing 1 required positional arg


def test_gotcha_omitting_parens_does_not_raise_at_decoration_time() -> None:
    # This is what makes the mistake insidious: no error at the @-line,
    # only later when you try to call the decorated function.
    errors_at_definition: list[str] = []

    def repeat(times: int):  # noqa: ARG001 — times unused; this example tests definition-time only
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> None:
                pass

            return wrapper

        return decorator

    try:

        @repeat  # type: ignore[arg-type]
        def greet() -> None:
            pass
    except Exception as exc:
        errors_at_definition.append(str(exc))

    # No exception was raised at definition time
    assert errors_at_definition == []
