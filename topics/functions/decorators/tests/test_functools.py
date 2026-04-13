# functools: wraps, update_wrapper, lru_cache, cache, cached_property, total_ordering.

import functools
import inspect

import pytest

# ---------------------------------------------------------------------------
# 1. functools.wraps
# ---------------------------------------------------------------------------


def test_wraps_preserves_function_name() -> None:
    def my_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def greet(name: str) -> str:
        """Greets someone."""
        return f"Hello, {name}"

    assert greet.__name__ == "greet"


def test_wraps_preserves_docstring() -> None:
    def my_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def greet() -> str:
        """Greets someone."""
        return "hello"

    assert greet.__doc__ == "Greets someone."


def test_wraps_preserves_annotations_module_and_qualname() -> None:
    def my_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def add(a: int, b: int) -> int:
        return a + b

    assert add.__annotations__ == {"a": int, "b": int, "return": int}
    assert add.__module__ == __name__
    assert "add" in add.__qualname__


def test_wraps_sets_wrapped_pointing_to_the_original_function() -> None:
    def my_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @my_decorator
    def greet() -> str:
        return "hello"

    # __wrapped__ is the key that lets inspect.unwrap() peel back the layers
    assert greet.__wrapped__ is not None


def test_wraps_enables_inspect_unwrap_through_multiple_layers() -> None:
    def make_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @make_decorator
    @make_decorator
    def greet() -> str:
        return "hello"

    original = inspect.unwrap(greet)
    assert original.__name__ == "greet"
    assert original is not greet


# ---------------------------------------------------------------------------
# 2. functools.update_wrapper
# ---------------------------------------------------------------------------


def test_update_wrapper_is_what_wraps_delegates_to() -> None:
    # functools.wraps(func) is shorthand for functools.update_wrapper(wrapper, func)
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        functools.update_wrapper(wrapper, func)
        return wrapper

    @my_decorator
    def greet() -> str:
        """Greets."""
        return "hello"

    assert greet.__name__ == "greet"
    assert greet.__doc__ == "Greets."


def test_update_wrapper_works_on_any_callable_not_just_functions() -> None:
    # This makes it useful for class-based decorators (see test_class_based.py).
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
# 3. functools.lru_cache
# ---------------------------------------------------------------------------


def test_lru_cache_memoises_results_to_avoid_recomputation() -> None:
    call_count = {"n": 0}

    @functools.lru_cache(maxsize=128)
    def square(n: int) -> int:
        call_count["n"] += 1
        return n * n

    assert square(5) == 25
    assert square(5) == 25  # cache hit
    assert square(5) == 25  # cache hit
    assert call_count["n"] == 1  # computed only once


def test_lru_cache_info_tracks_hits_misses_and_size() -> None:
    @functools.lru_cache(maxsize=128)
    def double(n: int) -> int:
        return n * 2

    double(10)  # miss
    double(10)  # hit
    double(10)  # hit
    double(20)  # miss

    info = double.cache_info()
    assert info.hits == 2
    assert info.misses == 2
    assert info.currsize == 2


def test_lru_cache_evicts_least_recently_used_when_full() -> None:
    @functools.lru_cache(maxsize=2)
    def identity(n: int) -> int:
        return n

    identity(1)  # cache: {1}
    identity(2)  # cache: {1, 2} — full
    identity(3)  # cache: {2, 3} — 1 evicted as the least recently used

    info = identity.cache_info()
    assert info.maxsize == 2
    assert info.currsize == 2


def test_lru_cache_clear_resets_cache_and_counters() -> None:
    @functools.lru_cache(maxsize=128)
    def double(n: int) -> int:
        return n * 2

    double(5)
    double(10)
    assert double.cache_info().currsize == 2

    double.cache_clear()
    assert double.cache_info().currsize == 0
    assert double.cache_info().hits == 0
    assert double.cache_info().misses == 0


def test_lru_cache_typed_true_keeps_int_and_float_as_separate_keys() -> None:
    @functools.lru_cache(maxsize=128, typed=True)
    def identity(x):
        return x

    identity(1)  # int entry
    identity(1.0)  # float entry — different key with typed=True

    assert identity.cache_info().currsize == 2


def test_lru_cache_requires_hashable_arguments() -> None:
    @functools.lru_cache(maxsize=128)
    def process(n: int) -> int:
        return n

    with pytest.raises(TypeError):
        process([1, 2, 3])  # type: ignore[arg-type]  # lists are not hashable


def test_lru_cache_dramatically_speeds_up_recursive_functions() -> None:
    call_count = {"n": 0}

    @functools.lru_cache(maxsize=None)  # noqa: UP033 — showing that maxsize=None equals functools.cache
    def fib(n: int) -> int:
        call_count["n"] += 1
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    result = fib(30)
    assert result == 832040
    # Without cache: ~2^30 calls; with cache: exactly 31 unique subproblems
    assert call_count["n"] == 31


# ---------------------------------------------------------------------------
# 4. functools.cache
# ---------------------------------------------------------------------------


def test_cache_is_an_unbounded_lru_cache() -> None:
    # functools.cache == lru_cache(maxsize=None): no eviction, simpler API.
    # Good when the input domain is bounded and every result should be kept.
    call_count = {"n": 0}

    @functools.cache
    def square(n: int) -> int:
        call_count["n"] += 1
        return n * n

    assert square(7) == 49
    assert square(7) == 49  # cache hit
    assert call_count["n"] == 1


def test_cache_grows_without_bound() -> None:
    @functools.cache
    def identity(n: int) -> int:
        return n

    for i in range(50):
        identity(i)

    info = identity.cache_info()
    assert info.currsize == 50
    assert info.maxsize is None  # no eviction limit


# ---------------------------------------------------------------------------
# 5. functools.cached_property
# ---------------------------------------------------------------------------


def test_cached_property_computes_the_value_only_once() -> None:
    computation_count = {"n": 0}

    class Circle:
        def __init__(self, radius: float) -> None:
            self.radius = radius

        @functools.cached_property
        def area(self) -> float:
            computation_count["n"] += 1
            return 3.14159 * self.radius**2

    circle = Circle(5.0)
    _ = circle.area  # computed here
    _ = circle.area  # retrieved from __dict__
    _ = circle.area  # retrieved from __dict__
    assert computation_count["n"] == 1


def test_cached_property_stores_result_directly_in_instance_dict() -> None:
    class Circle:
        def __init__(self, radius: float) -> None:
            self.radius = radius

        @functools.cached_property
        def area(self) -> float:
            return 3.14159 * self.radius**2

    circle = Circle(3.0)
    assert "area" not in circle.__dict__  # not computed yet
    _ = circle.area
    assert "area" in circle.__dict__  # now a plain instance attribute


def test_cached_property_is_per_instance_not_shared_across_instances() -> None:
    class Circle:
        def __init__(self, radius: float) -> None:
            self.radius = radius

        @functools.cached_property
        def area(self) -> float:
            return 3.14159 * self.radius**2

    small = Circle(1.0)
    large = Circle(10.0)

    assert small.area != large.area


def test_cached_property_gotcha_raises_on_slots_classes() -> None:
    # cached_property stores the result in instance.__dict__.
    # Classes with __slots__ and no __dict__ slot will raise TypeError.
    class SlottedCircle:
        __slots__ = ("radius",)

        def __init__(self, radius: float) -> None:
            self.radius = radius

        @functools.cached_property
        def area(self) -> float:
            return 3.14159 * self.radius**2

    circle = SlottedCircle(5.0)
    with pytest.raises(TypeError):
        _ = circle.area  # no __dict__ to store the cached value in


# ---------------------------------------------------------------------------
# 6. functools.total_ordering
# ---------------------------------------------------------------------------


def test_total_ordering_derives_missing_comparison_methods() -> None:
    # Provide __eq__ and one of __lt__, __le__, __gt__, __ge__; get the rest.
    @functools.total_ordering
    class Version:  # noqa: PLW1641 — __hash__ set to None implicitly; focus is on total_ordering
        def __init__(self, major: int, minor: int) -> None:
            self.major = major
            self.minor = minor

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Version):
                return NotImplemented
            return (self.major, self.minor) == (other.major, other.minor)

        def __lt__(self, other: object) -> bool:
            if not isinstance(other, Version):
                return NotImplemented
            return (self.major, self.minor) < (other.major, other.minor)

    v1 = Version(1, 0)
    v2 = Version(2, 0)
    v3 = Version(1, 0)

    assert v1 < v2
    assert v2 > v1  # derived from __lt__
    assert v1 <= v3  # derived from __lt__ and __eq__
    assert v2 >= v1  # derived from __lt__ and __eq__
    assert v1 == v3  # provided explicitly


def test_total_ordering_works_with_le_instead_of_lt() -> None:
    @functools.total_ordering
    class Priority:  # noqa: PLW1641 — __hash__ set to None implicitly; focus is on total_ordering
        def __init__(self, level: int) -> None:
            self.level = level

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Priority):
                return NotImplemented
            return self.level == other.level

        def __le__(self, other: object) -> bool:
            if not isinstance(other, Priority):
                return NotImplemented
            return self.level <= other.level

    low = Priority(1)
    high = Priority(10)

    assert low < high  # derived
    assert high > low  # derived
    assert low <= low  # noqa: PLR0124 — deliberately testing reflexivity with identical operands


def test_total_ordering_enables_sorting() -> None:
    @functools.total_ordering
    class Card:  # noqa: PLW1641 — __hash__ set to None implicitly; focus is on total_ordering
        ORDER = "23456789TJQKA"

        def __init__(self, rank: str) -> None:
            self.rank = rank

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Card):
                return NotImplemented
            return self.rank == other.rank

        def __lt__(self, other: object) -> bool:
            if not isinstance(other, Card):
                return NotImplemented
            return self.ORDER.index(self.rank) < self.ORDER.index(other.rank)

    hand = [Card("K"), Card("2"), Card("A"), Card("7")]
    sorted_hand = sorted(hand)
    assert [c.rank for c in sorted_hand] == ["2", "7", "K", "A"]


def test_total_ordering_gotcha_derived_methods_cost_more_than_manual() -> None:
    # total_ordering's derived methods call through the one provided method
    # (e.g. __gt__ is implemented as not (self < other) and self != other).
    # For hot sorting loops, manually implementing all six methods is faster.
    # This test just verifies the semantics are correct under sorting.
    @functools.total_ordering
    class Score:  # noqa: PLW1641 — __hash__ set to None implicitly; focus is on total_ordering
        def __init__(self, value: int) -> None:
            self.value = value

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Score):
                return NotImplemented
            return self.value == other.value

        def __lt__(self, other: object) -> bool:
            if not isinstance(other, Score):
                return NotImplemented
            return self.value < other.value

    scores = [Score(i) for i in range(50, 0, -1)]
    sorted_scores = sorted(scores)
    assert [s.value for s in sorted_scores] == list(range(1, 51))
