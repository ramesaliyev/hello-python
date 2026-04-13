# Decorator basics: the @-syntax, wrapping mechanics, side-effects, and identity loss.

import functools
import time

import pytest

# ---------------------------------------------------------------------------
# 1. Decorator protocol
# ---------------------------------------------------------------------------


def test_decorator_is_a_callable_that_takes_and_returns_a_callable() -> None:
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def greet(name: str) -> str:
        return f"Hello, {name}"

    # Manual application — exactly what @ does under the hood
    decorated = my_decorator(greet)
    assert decorated("Alice") == "Hello, Alice"


def test_at_syntax_is_sugar_for_manual_application() -> None:
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def greet(name: str) -> str:
        return f"Hello, {name}"

    # @my_decorator above is exactly: greet = my_decorator(greet)
    assert greet("Bob") == "Hello, Bob"


def test_decorator_runs_at_definition_time_not_call_time() -> None:
    decoration_log: list[str] = []

    def my_decorator(func):
        decoration_log.append(f"decorated {func.__name__}")

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    # The decorator runs immediately when the function definition is executed
    @my_decorator
    def greet() -> str:
        return "hello"

    assert decoration_log == ["decorated greet"]  # already ran, before any call
    greet()
    assert decoration_log == ["decorated greet"]  # still once — not per call


def test_decorator_replaces_the_name_in_the_namespace() -> None:
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def original() -> str:
        return "original"

    # `original` now refers to `wrapper`, not the original function
    assert original.__name__ == "wrapper"


# ---------------------------------------------------------------------------
# 2. Wrapping: forwarding args, kwargs, and return values
# ---------------------------------------------------------------------------


def test_wrapper_passes_through_positional_and_keyword_args() -> None:
    def passthrough(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @passthrough
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}"

    assert greet("Alice") == "Hello, Alice"
    assert greet("Alice", greeting="Hi") == "Hi, Alice"
    assert greet(name="Alice", greeting="Hey") == "Hey, Alice"


def test_wrapper_must_return_result_or_caller_silently_gets_none() -> None:
    def broken_passthrough(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)  # missing return — silent bug

        return wrapper

    @broken_passthrough
    def square(n: int) -> int:
        return n * n

    assert square(5) is None  # result is silently discarded


def test_decorator_can_transform_return_value() -> None:
    def double_result(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) * 2

        return wrapper

    @double_result
    def square(n: int) -> int:
        return n * n

    assert square(3) == 18  # (3 * 3) * 2


def test_decorator_can_normalise_arguments_before_calling() -> None:
    def abs_args(func):
        def wrapper(*args, **kwargs):
            normalised = tuple(abs(a) for a in args)
            return func(*normalised, **kwargs)

        return wrapper

    @abs_args
    def add(a: int, b: int) -> int:
        return a + b

    assert add(-3, -4) == 7


# ---------------------------------------------------------------------------
# 3. Side-effects: logging, counting, timing, validation, retrying
# ---------------------------------------------------------------------------


def test_decorator_can_log_every_call() -> None:
    call_log: list[str] = []

    def log_calls(func):
        def wrapper(*args, **kwargs):
            call_log.append(func.__name__)
            return func(*args, **kwargs)

        return wrapper

    @log_calls
    def greet(name: str) -> str:
        return f"Hello, {name}"

    greet("Alice")
    greet("Bob")
    assert call_log == ["greet", "greet"]


def test_decorator_can_count_calls_using_a_function_attribute() -> None:
    # Attaching state to the wrapper itself avoids needing a separate container.
    def count_calls(func):
        def wrapper(*args, **kwargs):
            wrapper.call_count += 1  # type: ignore[attr-defined]  # dynamic attribute set on the function object
            return func(*args, **kwargs)

        wrapper.call_count = 0  # type: ignore[attr-defined]  # dynamic attribute set on the function object
        return wrapper

    @count_calls
    def ping() -> str:
        return "pong"

    ping()
    ping()
    ping()
    assert ping.call_count == 3


def test_decorator_can_measure_execution_time() -> None:
    timings: list[float] = []

    def measure_time(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            timings.append(time.perf_counter() - start)
            return result

        return wrapper

    @measure_time
    def fast_work() -> str:
        return "done"

    fast_work()
    assert len(timings) == 1
    assert timings[0] >= 0


def test_decorator_can_validate_arguments() -> None:
    def require_positive(func):
        def wrapper(n: int) -> float:
            if n <= 0:
                raise ValueError(f"Expected a positive number, got {n}")
            return func(n)

        return wrapper

    @require_positive
    def sqrt_approx(n: int) -> float:
        return n**0.5

    assert sqrt_approx(4) == 2.0

    with pytest.raises(ValueError, match="Expected a positive number"):
        sqrt_approx(-1)


def test_decorator_is_useful_for_retrying_transient_failures() -> None:
    attempt_counter = {"n": 0}

    def retry_three_times(func):
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for _ in range(3):
                try:
                    return func(*args, **kwargs)
                except RuntimeError as exc:
                    last_exc = exc
            raise RuntimeError("All retries exhausted") from last_exc

        return wrapper

    @retry_three_times
    def flaky_service() -> str:
        attempt_counter["n"] += 1
        if attempt_counter["n"] < 3:
            raise RuntimeError("temporary failure")
        return "ok"

    assert flaky_service() == "ok"
    assert attempt_counter["n"] == 3


# ---------------------------------------------------------------------------
# 4. Decorating methods
# ---------------------------------------------------------------------------


def test_decorator_works_on_instance_methods_because_self_is_a_positional_arg() -> None:
    # `self` is passed as the first positional argument, so *args captures it
    # transparently — no special treatment needed for regular methods.
    calls: list[str] = []

    def log_calls(func):
        def wrapper(*args, **kwargs):
            calls.append(func.__name__)
            return func(*args, **kwargs)

        return wrapper

    class Counter:
        def __init__(self) -> None:
            self.value = 0

        @log_calls
        def increment(self) -> None:
            self.value += 1

    counter = Counter()
    counter.increment()
    counter.increment()
    assert counter.value == 2
    assert calls == ["increment", "increment"]


# ---------------------------------------------------------------------------
# 5. Gotcha: identity loss without functools.wraps
# ---------------------------------------------------------------------------


def test_bare_wrapper_loses_name_and_docstring() -> None:
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def important_function() -> None:
        """Does something important."""

    # Both __name__ and __doc__ now belong to `wrapper`, not the original.
    # This breaks logging, help(), error messages, and introspection tools.
    assert important_function.__name__ == "wrapper"
    assert important_function.__doc__ is None


def test_bare_wrapper_loses_annotations() -> None:
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def typed_function(x: int) -> str:
        return str(x)

    # Runtime type-checking tools and IDEs would see the wrong (empty) signature.
    assert typed_function.__annotations__ == {}


def test_functools_wraps_restores_identity() -> None:
    # functools.wraps copies metadata from the wrapped function onto the wrapper.
    # Full details are in test_functools.py; this shows the fix is one line.
    def my_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def important_function() -> None:
        """Does something important."""

    assert important_function.__name__ == "important_function"
    assert important_function.__doc__ == "Does something important."
    # __wrapped__ lets inspect.unwrap() reach the original
    assert important_function.__wrapped__ is not None
