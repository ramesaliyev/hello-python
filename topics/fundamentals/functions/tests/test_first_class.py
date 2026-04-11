# First-class functions, lambdas, and the callable protocol.
# Functions are objects: they can be assigned, stored, passed, and returned.


from collections.abc import Callable
from functools import reduce

import pytest

# ---------------------------------------------------------------------------
# 1. Functions are objects
# ---------------------------------------------------------------------------


def test_function_can_be_assigned_to_variable() -> None:
    def greet(name: str) -> str:
        return f"hello {name}"

    say_hello = greet  # binding, not calling
    assert say_hello("alice") == "hello alice"
    assert say_hello is greet


def test_function_has_attributes() -> None:
    def my_func() -> None:
        """My docstring."""

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "My docstring."


def test_functions_can_be_stored_in_a_list() -> None:
    def double(x: int) -> int:
        return x * 2

    def triple(x: int) -> int:
        return x * 3

    ops = [double, triple]
    assert [f(4) for f in ops] == [8, 12]


def test_functions_can_be_stored_in_a_dict() -> None:
    ops = {
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
    }
    assert ops["add"](3, 4) == 7
    assert ops["sub"](10, 3) == 7


# ---------------------------------------------------------------------------
# 2. Passing functions as arguments (higher-order functions / callbacks)
# ---------------------------------------------------------------------------


def test_function_passed_as_argument() -> None:
    def apply(func: Callable[[int], int], value: int) -> int:
        return func(value)

    assert apply(abs, -5) == 5


def test_callback_invoked_inside_caller() -> None:
    def run_twice(callback: Callable[[], str]) -> list[str]:
        return [callback(), callback()]

    results = run_twice(lambda: "ping")
    assert results == ["ping", "ping"]


def test_sorted_with_key_function() -> None:
    words = ["banana", "fig", "apple", "kiwi"]
    assert sorted(words, key=len) == ["fig", "kiwi", "apple", "banana"]


def test_max_with_key_function() -> None:
    pairs = [(1, 5), (3, 2), (2, 8)]
    assert max(pairs, key=lambda p: p[1]) == (2, 8)  # max by second element


# ---------------------------------------------------------------------------
# 3. Returning functions (factory functions)
# ---------------------------------------------------------------------------


def test_function_returned_from_function() -> None:
    def make_greeter(greeting: str) -> Callable[[str], str]:
        def greeter(name: str) -> str:
            return f"{greeting}, {name}!"

        return greeter

    hi = make_greeter("hi")
    hey = make_greeter("hey")
    assert hi("alice") == "hi, alice!"
    assert hey("bob") == "hey, bob!"


def test_factory_returns_different_functions_each_time() -> None:
    def make_adder(n: int) -> Callable[[int], int]:
        return lambda x: x + n

    add1 = make_adder(1)
    add2 = make_adder(2)
    assert add1 is not add2
    assert add1(10) == 11
    assert add2(10) == 12


# ---------------------------------------------------------------------------
# 4. Function composition
# ---------------------------------------------------------------------------


def test_manual_function_composition() -> None:
    def compose(
        f: Callable[[int], int], g: Callable[[int], int]
    ) -> Callable[[int], int]:
        return lambda x: f(g(x))

    add1 = lambda x: x + 1  # noqa: E731 — lambda assignment is the subject of this test
    double = lambda x: x * 2  # noqa: E731 — lambda assignment is the subject of this test

    add1_then_double = compose(double, add1)  # double(add1(x))
    assert add1_then_double(3) == 8  # add1(3)=4, double(4)=8


def test_pipeline_via_reduce() -> None:
    def pipeline(*fns: Callable[[int], int]) -> Callable[[int], int]:
        return reduce(lambda f, g: lambda x: g(f(x)), fns)

    process = pipeline(lambda x: x + 1, lambda x: x * 2, lambda x: x - 3)
    assert process(4) == 7  # (4+1)*2 - 3 = 7


# ---------------------------------------------------------------------------
# 5. Lambda expressions
# ---------------------------------------------------------------------------


def test_lambda_is_an_anonymous_function() -> None:
    square: Callable[[int], int] = lambda x: x**2  # noqa: E731 — lambda assignment is the subject of this test
    assert square(5) == 25


def test_lambda_can_take_multiple_args() -> None:
    add: Callable[[int, int], int] = lambda x, y: x + y  # noqa: E731 — lambda assignment is the subject of this test
    assert add(3, 4) == 7


def test_lambda_body_must_be_a_single_expression() -> None:
    # Lambdas cannot contain statements (assignment, return, if-blocks, etc.)
    # This is a SyntaxError at parse time:
    with pytest.raises(SyntaxError):
        eval("lambda x: x = 1")  # noqa: S307  # eval is intentional here to trigger SyntaxError


def test_lambda_has_no_docstring() -> None:
    f = lambda x: x  # noqa: E731 — lambda assignment is the subject of this test
    assert f.__doc__ is None


def test_lambda_name_is_lambda() -> None:
    # This makes tracebacks and introspection less informative than named functions
    f = lambda x: x  # noqa: E731 — lambda assignment is the subject of this test
    assert f.__name__ == "<lambda>"


def test_lambda_used_as_sort_key() -> None:
    data: list[dict[str, int | str]] = [
        {"name": "charlie", "age": 30},
        {"name": "alice", "age": 25},
    ]
    sorted_data = sorted(data, key=lambda d: d["age"])
    assert sorted_data[0]["name"] == "alice"


# ---------------------------------------------------------------------------
# 6. Lambda late-binding-in-loops gotcha
# ---------------------------------------------------------------------------


def test_lambda_in_loop_captures_variable_by_reference() -> None:
    # `i` is resolved when the lambda is *called*, not when it is created.
    # After the loop, `i` is 2 for every lambda.
    lambdas = [lambda: i for i in range(3)]  # noqa: B023
    assert lambdas[0]() == 2  # NOT 0
    assert lambdas[1]() == 2  # NOT 1


def test_lambda_late_binding_fixed_with_default_argument() -> None:
    # Capture the current value via a default argument — evaluated at definition time
    lambdas = [lambda i=i: i for i in range(3)]
    assert lambdas[0]() == 0
    assert lambdas[1]() == 1
    assert lambdas[2]() == 2


# ---------------------------------------------------------------------------
# 7. callable()
# ---------------------------------------------------------------------------


def test_callable_returns_true_for_functions() -> None:
    def f() -> None:
        pass

    assert callable(f)


def test_callable_returns_true_for_lambdas() -> None:
    assert callable(lambda: None)


def test_callable_returns_true_for_classes() -> None:
    # Classes are callable — calling them creates an instance
    class MyClass:
        pass

    assert callable(MyClass)


def test_callable_returns_false_for_plain_objects() -> None:
    assert not callable(42)
    assert not callable("hello")
    assert not callable([1, 2, 3])


def test_callable_returns_true_for_objects_with_dunder_call() -> None:
    class Multiplier:
        def __init__(self, factor: int) -> None:
            self.factor = factor

        def __call__(self, x: int) -> int:
            return x * self.factor

    double = Multiplier(2)
    assert callable(double)
    assert double(5) == 10
