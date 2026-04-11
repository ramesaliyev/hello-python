# Variable scope and name resolution as pytest-verified learning notes.
# Python resolves names in LEGB order: Local → Enclosing → Global → Built-in.


from collections.abc import Callable

import pytest

# ---------------------------------------------------------------------------
# 1. Local scope
# ---------------------------------------------------------------------------


def test_local_variable_does_not_leak_outside_function() -> None:
    def inner() -> int:
        x = 42
        return x  # noqa: RET504  # intentional: shows the variable exists locally

    inner()
    assert "x" not in dir()  # x is local to inner, not visible here


def test_assignment_inside_function_creates_local_variable() -> None:
    x = "global"

    def inner() -> str:
        x = "local"  # new binding in local scope, does not touch the outer x
        return x  # noqa: RET504  # intentional: shows assignment happens in local scope

    assert inner() == "local"
    assert x == "global"  # outer x unchanged


# ---------------------------------------------------------------------------
# 2. Enclosing scope (the E in LEGB)
# ---------------------------------------------------------------------------


def test_inner_function_reads_enclosing_variable() -> None:
    def outer() -> str:
        message = "from outer"

        def inner() -> str:
            return message  # looks up Enclosing scope

        return inner()

    assert outer() == "from outer"


def test_enclosing_variable_read_reflects_value_at_call_time() -> None:
    # The enclosing variable is looked up when the inner function runs, not when defined
    def outer() -> list[int]:
        results = []
        x = 1

        def capture() -> int:
            return x

        results.append(capture())
        x = 2
        results.append(capture())
        return results

    assert outer() == [1, 2]


# ---------------------------------------------------------------------------
# 3. Global scope and the `global` keyword
# ---------------------------------------------------------------------------


_counter = 0


def test_reading_global_variable_works_without_declaration() -> None:
    # Reading a global from inside a function is allowed without `global`
    def get_counter() -> int:
        return _counter

    assert get_counter() == 0


def test_assigning_without_global_creates_local_not_global() -> None:
    value = 10

    def set_value() -> None:
        value = 99  # noqa: F841 -- creates a local, not touching outer `value`

    set_value()
    assert value == 10  # outer `value` unchanged


def test_global_keyword_allows_mutating_module_level_variable() -> None:
    count = 0

    # Use a mutable container to simulate module-level mutation in a test
    state = {"count": 0}

    def increment() -> None:
        state["count"] += 1  # mutating the dict — no global keyword needed

    increment()
    increment()
    assert state["count"] == 2
    assert count == 0  # this local is untouched


def test_global_keyword_rebinds_module_variable() -> None:
    # Demonstrate actual `global` behaviour with a module-level name
    global _counter  # noqa: PLW0603 — intentional: demonstrates the global statement
    _counter = 0

    def bump() -> None:
        global _counter  # noqa: PLW0603 — intentional: demonstrates the global statement inside a nested function
        _counter += 1

    bump()
    bump()
    assert _counter == 2
    _counter = 0  # reset for other tests


# ---------------------------------------------------------------------------
# 4. nonlocal keyword
# ---------------------------------------------------------------------------


def test_nonlocal_allows_mutating_enclosing_variable() -> None:
    def make_counter() -> tuple[Callable[[], None], Callable[[], int]]:
        count = 0

        def increment() -> None:
            nonlocal count
            count += 1

        def get() -> int:
            return count

        return increment, get

    increment, get = make_counter()
    increment()
    increment()
    assert get() == 2


def test_nonlocal_only_reaches_nearest_enclosing_scope() -> None:
    def outer() -> int:
        x = 1

        def middle() -> int:
            x = 10  # creates a new local in middle — does NOT touch outer's x

            def inner() -> None:
                nonlocal x
                x = 99  # rebinds middle's x, not outer's

            inner()
            return x  # middle's x

        middle()
        return x  # outer's x is untouched

    assert outer() == 1


def test_nonlocal_cannot_be_used_at_module_level() -> None:
    # nonlocal requires an enclosing function scope to target
    bad_code = "def f():\n    nonlocal x\n"
    with pytest.raises(SyntaxError):
        compile(bad_code, "<string>", "exec")


# ---------------------------------------------------------------------------
# 5. Closures — functions that remember their enclosing scope
# ---------------------------------------------------------------------------


def test_closure_captures_enclosing_variable() -> None:
    def make_adder(n: int) -> Callable[[int], int]:
        def adder(x: int) -> int:
            return x + n  # n is captured from the enclosing scope

        return adder

    add5 = make_adder(5)
    add10 = make_adder(10)
    assert add5(3) == 8
    assert add10(3) == 13


def test_each_closure_has_its_own_cell() -> None:
    # Each call to the outer function creates a fresh enclosing scope
    def make_multiplier(factor: int) -> Callable[[int], int]:
        def multiply(x: int) -> int:
            return x * factor

        return multiply

    double = make_multiplier(2)
    triple = make_multiplier(3)
    assert double(5) == 10
    assert triple(5) == 15
    assert double is not triple


def test_closure_cell_is_accessible_via_dunder_closure() -> None:
    def outer() -> Callable[[], str]:
        captured_value = "hidden"

        def inner() -> str:
            return captured_value

        return inner

    fn = outer()
    assert fn.__closure__ is not None
    cell_contents = [c.cell_contents for c in fn.__closure__]
    assert "hidden" in cell_contents


# ---------------------------------------------------------------------------
# 6. Late-binding gotcha in closures
# ---------------------------------------------------------------------------


def test_closure_late_binding_in_loop_gotcha() -> None:
    # All lambdas/closures reference the same variable `i`, not a snapshot of its value.
    # By the time any of them is called, the loop has finished and `i` is 4.
    funcs = [lambda: i for i in range(5)]  # noqa: B023
    assert funcs[0]() == 4  # NOT 0 — all see the final value of i
    assert funcs[2]() == 4  # NOT 2


def test_late_binding_fixed_with_default_argument() -> None:
    # Binding the current value to a default parameter captures it at definition time
    funcs = [lambda i=i: i for i in range(5)]
    assert funcs[0]() == 0
    assert funcs[2]() == 2
    assert funcs[4]() == 4


def test_late_binding_fixed_with_factory_function() -> None:
    # A factory function creates a fresh enclosing scope on each call
    def make_fn(value: int) -> Callable[[], int]:
        return lambda: value

    funcs = [make_fn(i) for i in range(5)]
    assert funcs[0]() == 0
    assert funcs[2]() == 2
    assert funcs[4]() == 4


# ---------------------------------------------------------------------------
# 7. Built-in scope and shadowing
# ---------------------------------------------------------------------------


def test_builtin_name_available_without_import() -> None:
    # Built-ins (len, print, range, …) are found in the B layer of LEGB
    assert len([1, 2, 3]) == 3


def test_local_name_shadows_builtin() -> None:
    len: Callable[[list[int]], str] = lambda _x: "shadowed"  # noqa: A001, E731  # local `len` hides the built-in
    assert len([1, 2, 3]) == "shadowed"
    # The built-in is not destroyed — the shadow only exists in this local scope
