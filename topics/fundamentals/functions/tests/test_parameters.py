# Function parameter kinds and argument-passing rules as pytest-verified learning notes.
# Python has five distinct parameter kinds; their ordering is enforced by the parser.


import pytest

# ---------------------------------------------------------------------------
# 1. Positional and keyword arguments
# ---------------------------------------------------------------------------


def test_positional_args_are_order_dependent() -> None:
    def greet(first: str, second: str) -> str:
        return f"{first} {second}"

    assert greet("hello", "world") == "hello world"
    assert greet("world", "hello") == "world hello"  # order changed → result changes


def test_keyword_args_can_be_passed_in_any_order() -> None:
    def greet(first: str, second: str) -> str:
        return f"{first} {second}"

    assert greet(second="world", first="hello") == "hello world"


def test_positional_and_keyword_can_be_mixed() -> None:
    # Positional args must come before keyword args at the call site
    def greet(first: str, second: str) -> str:
        return f"{first} {second}"

    assert greet("hello", second="world") == "hello world"


# ---------------------------------------------------------------------------
# 2. Default parameter values
# ---------------------------------------------------------------------------


def test_default_value_used_when_arg_is_omitted() -> None:
    def greet(name: str, greeting: str = "hello") -> str:
        return f"{greeting} {name}"

    assert greet("alice") == "hello alice"
    assert greet("alice", "hi") == "hi alice"


def test_default_value_evaluated_once_at_definition_time() -> None:
    # The default is bound to the function object when def runs, not on each call.
    # This is the famous mutable-default gotcha: all callers share the same object.
    def append_to(item: int, lst: list[int] = []) -> list[int]:  # noqa: B006
        lst.append(item)
        return lst

    first_call = append_to(1)
    second_call = append_to(2)  # reuses the same default list!
    assert first_call is second_call  # same object
    assert first_call == [1, 2]  # mutation accumulated across calls


def test_none_sentinel_avoids_mutable_default_gotcha() -> None:
    # The idiomatic fix: use None as default and create a fresh object inside
    def append_to(item: int, lst: list[int] | None = None) -> list[int]:
        if lst is None:
            lst = []
        lst.append(item)
        return lst

    first_call = append_to(1)
    second_call = append_to(2)
    assert first_call is not second_call  # independent lists
    assert first_call == [1]
    assert second_call == [2]


# ---------------------------------------------------------------------------
# 3. *args — variadic positional arguments
# ---------------------------------------------------------------------------


def test_args_collects_extra_positional_into_tuple() -> None:
    def total(*args: int) -> int:
        return sum(args)

    assert total(1, 2, 3) == 6
    assert total() == 0  # zero extra args → empty tuple


def test_args_is_always_a_tuple() -> None:
    def capture(*args: int) -> tuple[int, ...]:
        return args

    assert isinstance(capture(1, 2, 3), tuple)


def test_iterable_can_be_unpacked_into_args() -> None:
    def total(*args: int) -> int:
        return sum(args)

    nums = [1, 2, 3]
    assert total(*nums) == 6


# ---------------------------------------------------------------------------
# 4. **kwargs — variadic keyword arguments
# ---------------------------------------------------------------------------


def test_kwargs_collects_extra_keyword_args_into_dict() -> None:
    def capture(**kwargs: int) -> dict[str, int]:
        return kwargs

    assert capture(a=1, b=2) == {"a": 1, "b": 2}
    assert capture() == {}


def test_dict_can_be_unpacked_into_kwargs() -> None:
    def greet(first: str, second: str) -> str:
        return f"{first} {second}"

    data = {"first": "hello", "second": "world"}
    assert greet(**data) == "hello world"


def test_args_and_kwargs_together() -> None:
    def echo(*args: int, **kwargs: str) -> tuple[tuple[int, ...], dict[str, str]]:
        return args, kwargs

    pos, kw = echo(1, 2, x="a", y="b")
    assert pos == (1, 2)
    assert kw == {"x": "a", "y": "b"}


# ---------------------------------------------------------------------------
# 5. Positional-only parameters  /  (PEP 570, Python 3.8+)
# ---------------------------------------------------------------------------


def test_positional_only_params_cannot_be_passed_by_keyword() -> None:
    # Everything before / is positional-only
    def add(x: int, y: int, /) -> int:
        return x + y

    assert add(1, 2) == 3

    with pytest.raises(TypeError, match="keyword argument"):
        add(x=1, y=2)  # type: ignore[call-arg]


def test_positional_only_name_can_be_reused_in_kwargs() -> None:
    # Because x is positional-only, **kwargs may have a key named "x" without conflict
    def func(x: int, /, **kwargs: int) -> tuple[int, dict[str, int]]:
        return x, kwargs

    result = func(1, x=99)  # outer x → positional slot; inner x → kwargs dict
    assert result == (1, {"x": 99})


# ---------------------------------------------------------------------------
# 6. Keyword-only parameters  *  (PEP 3102)
# ---------------------------------------------------------------------------


def test_keyword_only_params_must_be_passed_by_keyword() -> None:
    # Everything after the bare * (or after *args) is keyword-only
    def connect(host: str, *, port: int, timeout: int = 30) -> str:
        return f"{host}:{port} t={timeout}"

    assert connect("localhost", port=8080) == "localhost:8080 t=30"

    with pytest.raises(TypeError, match="keyword"):
        connect("localhost", 8080)  # type: ignore[misc]


def test_keyword_only_after_args() -> None:
    def func(*args: int, sep: str = "-") -> str:
        return sep.join(str(a) for a in args)

    assert func(1, 2, 3) == "1-2-3"
    assert func(1, 2, 3, sep=":") == "1:2:3"


# ---------------------------------------------------------------------------
# 7. Combining all parameter kinds — legal ordering
# ---------------------------------------------------------------------------


def test_full_signature_ordering() -> None:
    # Legal order: positional-only / , regular, *args, keyword-only, **kwargs
    def full(
        pos_only: int,
        /,
        regular: int,
        *args: int,
        kw_only: int,
        **kwargs: int,
    ) -> dict[str, object]:
        return {
            "pos_only": pos_only,
            "regular": regular,
            "args": args,
            "kw_only": kw_only,
            "kwargs": kwargs,
        }

    result = full(1, 2, 3, 4, kw_only=5, extra=6)
    assert result["pos_only"] == 1
    assert result["regular"] == 2
    assert result["args"] == (3, 4)
    assert result["kw_only"] == 5
    assert result["kwargs"] == {"extra": 6}


def test_mixing_positional_only_and_keyword_only() -> None:
    # / and * can both appear in the same signature
    def func(a: int, b: int, /, *, c: int, d: int) -> int:
        return a + b + c + d

    assert func(1, 2, c=3, d=4) == 10

    with pytest.raises(TypeError):
        func(a=1, b=2, c=3, d=4)  # type: ignore[call-arg]  # a and b are positional-only
