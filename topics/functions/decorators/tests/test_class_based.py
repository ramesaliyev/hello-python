# Class-based decorators: __call__, stateful decoration, __get__, and class decorators.

import functools
import inspect
import types

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class CallCounter:
    """Decorator that counts how many times the wrapped function is called."""

    def __init__(self, func) -> None:
        functools.update_wrapper(self, func)
        self._func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self._func(*args, **kwargs)


# ---------------------------------------------------------------------------
# 1. Class-as-decorator via __call__
# ---------------------------------------------------------------------------


def test_class_with_call_can_be_used_as_a_decorator() -> None:
    # __init__ receives the function to wrap; __call__ is the replacement wrapper.
    class Passthrough:
        def __init__(self, func) -> None:
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

    @Passthrough
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5


def test_class_based_decorator_produces_an_instance_not_a_function() -> None:
    class Passthrough:
        def __init__(self, func) -> None:
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

    @Passthrough
    def greet() -> str:
        return "hello"

    assert isinstance(greet, Passthrough)


def test_update_wrapper_preserves_identity_on_class_based_decorators() -> None:
    class Passthrough:
        def __init__(self, func) -> None:
            functools.update_wrapper(self, func)
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

    @Passthrough
    def greet() -> str:
        """Says hello."""
        return "hello"

    assert greet.__name__ == "greet"  # type: ignore[attr-defined]  # __name__ is copied by update_wrapper; not in Passthrough's static type
    assert greet.__doc__ == "Says hello."


# ---------------------------------------------------------------------------
# 2. Stateful decorators
# ---------------------------------------------------------------------------


def test_class_based_decorator_holds_state_naturally_in_instance_attributes() -> None:
    # A function-based decorator needs a mutable container or nonlocal for state.
    # A class-based decorator stores state directly in self.
    @CallCounter
    def ping() -> str:
        return "pong"

    ping()
    ping()
    ping()
    assert ping.count == 3


def test_each_decorated_function_has_its_own_independent_counter() -> None:
    @CallCounter
    def foo() -> None:
        pass

    @CallCounter
    def bar() -> None:
        pass

    foo()
    foo()
    bar()
    assert foo.count == 2
    assert bar.count == 1


def test_class_based_decorator_can_accumulate_return_values() -> None:
    class ResultRecorder:
        def __init__(self, func) -> None:
            functools.update_wrapper(self, func)
            self._func = func
            self.history: list = []

        def __call__(self, *args, **kwargs):
            result = self._func(*args, **kwargs)
            self.history.append(result)
            return result

    @ResultRecorder
    def square(n: int) -> int:
        return n * n

    square(2)
    square(3)
    square(4)
    assert square.history == [4, 9, 16]


# ---------------------------------------------------------------------------
# 3. Gotcha: class-based decorator breaks method binding without __get__
# ---------------------------------------------------------------------------
#
# Why does `self` work at all for regular methods?
#
#   First: in Python, functions are objects too.  `def greet(self): ...`
#   creates a function object and stores it in MyClass.__dict__["greet"].
#   That function object has its own __get__ method built into it (all
#   function objects do — it is part of Python's function type).
#
#   Every time you write `obj.greet`, Python runs this lookup sequence:
#     1. Search obj.__dict__ for "greet" — this is the instance's own data
#        (things assigned as self.x = ... in __init__).  Methods defined in
#        the class body are not there; they live in the class dict.  Not found.
#     2. Search MyClass.__dict__ — found the function object at "greet".
#     3. Does that object define __get__?  Functions do → call it:
#          greet.__get__(obj, MyClass)  →  returns a bound method
#     4. The bound method is returned — NOT the raw function.
#
#   A bound method prepends `obj` as the first argument on every call.
#   So `obj.greet(a, b)` becomes `greet(obj, a, b)` under the hood —
#   or more precisely: greet(obj, *args, **kwargs).
#   Steps 1-4 happen on every attribute access, every time, at runtime.
#
# What goes wrong with a class-based decorator:
#
#   The decorator replaces the function with a plain object that has no
#   __get__.  Step 3 above finds nothing, so Python skips it and returns
#   the decorator object as-is.  `obj.greet` is then the raw decorator —
#   same object as `MyClass.greet`, with no instance attached.
#
#   Calling `obj.greet()` is therefore `decorator()` with zero arguments.
#   Inside __call__, `self._func()` runs with nothing, but the original
#   `greet` still expects a MyClass instance as `self` → TypeError.


def test_class_based_decorator_breaks_self_on_instance_methods() -> None:
    class NoGetDecorator:
        def __init__(self, func) -> None:
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

    class MyClass:
        @NoGetDecorator
        def greet(self) -> str:
            return f"hello from {type(self).__name__}"

    obj = MyClass()
    with pytest.raises(TypeError):
        # obj.greet returns the decorator instance (no __get__, no binding).
        # Calling it passes zero arguments to NoGetDecorator.__call__, which
        # then calls greet() with no args — missing the required `self`.
        obj.greet()


def test_without_get_instance_and_class_access_return_the_same_object() -> None:
    class NoGetDecorator:
        def __init__(self, func) -> None:
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

    class MyClass:
        @NoGetDecorator
        def greet(self) -> str:
            return "hello"

    # Both return the identical decorator instance — no binding ever happened.
    # For a regular function, MyClass.greet would return the function, while
    # obj.greet would return a bound method wrapping it. Here they are the same.
    assert isinstance(MyClass.greet, NoGetDecorator)
    assert MyClass().greet is MyClass.greet  # same object, obj was never captured


# ---------------------------------------------------------------------------
# 4. Fix: implement __get__ to restore method binding
# ---------------------------------------------------------------------------
#
# Adding __get__ re-enrolls the decorator in the same lookup protocol that
# plain functions use.  Python will now call it when attribute access happens.
#
#   __get__(self, obj, objtype)
#     self     — the decorator instance (stored in the class dict)
#     obj      — the instance the attribute was accessed through,
#                or None when accessed directly on the class
#     objtype  — the class (MyClass)
#
# When obj is not None, return types.MethodType(self, obj).
#   MethodType creates a callable that prepends `obj` to every call —
#   the same thing a bound method does for plain functions.
#
# When obj is None (e.g. `MyClass.greet`), return self so the decorator
#   object is still reachable — useful for reading attributes like .count.


def test_implementing_get_restores_correct_self_binding() -> None:
    class MethodAwareDecorator:
        def __init__(self, func) -> None:
            functools.update_wrapper(self, func)
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self  # class-level access — return the decorator itself
            # types.MethodType(self, obj) produces a bound-method-like callable;
            # when called, it prepends `obj` as the first argument to __call__.
            return types.MethodType(self, obj)

    class MyClass:
        @MethodAwareDecorator
        def greet(self) -> str:
            return f"hello from {type(self).__name__}"

    obj = MyClass()
    assert obj.greet() == "hello from MyClass"


def test_get_returns_self_for_class_level_access() -> None:
    class MethodAwareDecorator:
        def __init__(self, func) -> None:
            self._func = func

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return types.MethodType(self, obj)

    class MyClass:
        @MethodAwareDecorator
        def greet(self) -> str:
            return "hello"

    # Accessing via the class (no instance) returns the decorator itself
    assert isinstance(MyClass.greet, MethodAwareDecorator)


def test_method_aware_decorator_maintains_call_count_across_instances() -> None:
    class CountingDecorator:
        def __init__(self, func) -> None:
            functools.update_wrapper(self, func)
            self._func = func
            self.count = 0

        def __call__(self, *args, **kwargs):
            self.count += 1
            return self._func(*args, **kwargs)

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return types.MethodType(self, obj)

    class MyClass:
        @CountingDecorator
        def work(self) -> None:
            pass

    obj_a = MyClass()
    obj_b = MyClass()
    obj_a.work()
    obj_a.work()
    obj_b.work()

    # The count lives on the single decorator instance shared by the class
    assert MyClass.work.count == 3


# ---------------------------------------------------------------------------
# 5. Decorating a class
# ---------------------------------------------------------------------------


def test_class_decorator_can_add_a_method_to_a_class() -> None:
    # A decorator can take a *class* as its argument and return a modified class.
    def add_repr(cls):
        def __repr__(self) -> str:  # noqa: N807 — teaching a decorator that installs a dunder method
            attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            return f"{type(self).__name__}({attrs})"

        cls.__repr__ = __repr__
        return cls

    @add_repr
    class Point:
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    assert repr(Point(1.0, 2.0)) == "Point(x=1.0, y=2.0)"


def test_class_decorator_can_enforce_constraints_at_definition_time() -> None:
    # Class decorators run when the class body is executed — ideal for validation
    # that would otherwise only surface at instantiation time or later.
    def require_docstring(cls):
        if not cls.__doc__:
            raise TypeError(f"{cls.__name__} must have a docstring")
        return cls

    @require_docstring
    class WellDocumented:
        """This class is properly documented."""

    with pytest.raises(TypeError, match="must have a docstring"):

        @require_docstring
        class PoorlyDocumented:
            pass


def test_class_decorator_can_register_classes_in_a_central_registry() -> None:
    # A common pattern for plugin systems, command registries, and event handlers.
    registry: dict[str, type] = {}

    def register(cls):
        registry[cls.__name__] = cls
        return cls

    @register
    class Alpha:
        pass

    @register
    class Beta:
        pass

    assert "Alpha" in registry
    assert "Beta" in registry
    assert registry["Alpha"] is Alpha


def test_class_decorator_can_wrap_all_methods_automatically() -> None:
    # A class decorator can iterate over all methods with inspect and apply
    # a wrapper to each one — a convenient way to add cross-cutting concerns
    # (logging, timing, rate-limiting) without touching the class body at all.

    def log_calls(cls):
        log: list[str] = []

        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Default-argument capture avoids the late-binding closure trap.
            @functools.wraps(method)
            def wrapper(*args, _name=name, _method=method, **kwargs):
                log.append(_name)
                return _method(*args, **kwargs)

            setattr(cls, name, wrapper)

        cls.call_log = log
        return cls

    @log_calls
    class Greeter:
        def hello(self) -> str:
            return "hello"

        def goodbye(self) -> str:
            return "goodbye"

    g = Greeter()
    g.hello()
    g.goodbye()
    g.hello()

    assert Greeter.call_log == ["hello", "goodbye", "hello"]  # type: ignore[attr-defined]


def test_class_decorator_can_implement_singleton_pattern() -> None:
    # The decorator replaces the class itself with a factory function that
    # caches the first instance and returns it on every subsequent call.
    def singleton(cls):
        instance = None

        @functools.wraps(cls)
        def get_instance(*args, **kwargs):
            nonlocal instance
            if instance is None:
                instance = cls(*args, **kwargs)
            return instance

        return get_instance

    @singleton
    class Config:
        def __init__(self, value: int) -> None:
            self.value = value

    first = Config(1)
    second = Config(99)  # different args — still returns the first instance

    assert first is second
    assert first.value == 1
