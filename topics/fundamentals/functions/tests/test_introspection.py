# Function introspection as pytest-verified learning notes.
# Python exposes rich metadata on function objects via dunder attributes and inspect.


from collections.abc import Callable, Generator
import inspect

# ---------------------------------------------------------------------------
# 1. Identity attributes — __name__, __qualname__, __module__
# ---------------------------------------------------------------------------


def test_dunder_name_holds_function_name() -> None:
    def my_function() -> None:
        pass

    assert my_function.__name__ == "my_function"


def test_lambda_name_is_angle_lambda() -> None:
    f = lambda: None  # noqa: E731 — lambda assignment is the subject of this test
    assert f.__name__ == "<lambda>"


def test_dunder_qualname_includes_enclosing_scope() -> None:
    def outer() -> Callable[[], None]:
        def inner() -> None:
            pass

        return inner

    inner_fn = outer()
    # qualname shows the full dotted path within the module
    expected = (
        "test_dunder_qualname_includes_enclosing_scope.<locals>.outer.<locals>.inner"
    )
    assert inner_fn.__qualname__ == expected


def test_dunder_module_is_the_defining_modules_name() -> None:
    def f() -> None:
        pass

    assert isinstance(f.__module__, str)
    assert f.__module__ != ""


# ---------------------------------------------------------------------------
# 2. Documentation — __doc__
# ---------------------------------------------------------------------------


def test_dunder_doc_holds_docstring() -> None:
    def documented() -> None:
        """This is the docstring."""

    assert documented.__doc__ == "This is the docstring."


def test_dunder_doc_is_none_without_docstring() -> None:
    def undocumented() -> None:
        pass

    assert undocumented.__doc__ is None


# ---------------------------------------------------------------------------
# 3. Type annotations — __annotations__
# ---------------------------------------------------------------------------


def test_dunder_annotations_holds_parameter_and_return_hints() -> None:
    def add(x: int, y: int) -> int:
        return x + y

    assert add.__annotations__ == {"x": int, "y": int, "return": int}


def test_dunder_annotations_is_empty_without_hints() -> None:
    def no_hints(x, y):  # intentionally unannotated
        return x + y

    assert no_hints.__annotations__ == {}


def test_annotations_do_not_enforce_types_at_runtime() -> None:
    def typed(x: int) -> int:
        return x

    # Python does not validate types at runtime — strings pass just fine
    result = typed("not an int")  # type: ignore[arg-type]
    assert result == "not an int"  # type: ignore[comparison-overlap]


# ---------------------------------------------------------------------------
# 4. Default values — __defaults__ and __kwdefaults__
# ---------------------------------------------------------------------------


def test_dunder_defaults_holds_positional_defaults_as_tuple() -> None:
    def greet(name: str, greeting: str = "hello", punct: str = "!") -> str:
        return f"{greeting} {name}{punct}"

    # __defaults__ contains only the values, in declaration order
    assert greet.__defaults__ == ("hello", "!")


def test_dunder_defaults_is_none_when_no_defaults_exist() -> None:
    def no_defaults(x: int, y: int) -> int:
        return x + y

    assert no_defaults.__defaults__ is None


def test_dunder_kwdefaults_holds_keyword_only_defaults() -> None:
    def func(*, sep: str = "-", end: str = "\n") -> str:
        return sep + end

    assert func.__kwdefaults__ == {"sep": "-", "end": "\n"}


def test_dunder_kwdefaults_is_none_when_no_kw_only_defaults() -> None:
    def func(*, required: str) -> str:
        return required

    assert func.__kwdefaults__ is None


# ---------------------------------------------------------------------------
# 5. Closure cells — __closure__
# ---------------------------------------------------------------------------


def test_dunder_closure_is_none_for_non_closure() -> None:
    def plain() -> int:
        return 42

    assert plain.__closure__ is None


def test_dunder_closure_contains_cells_for_captured_variables() -> None:
    def outer(x: int) -> Callable[[], int]:
        def inner() -> int:
            return x

        return inner

    inner_fn = outer(99)
    assert inner_fn.__closure__ is not None
    cell_contents = [c.cell_contents for c in inner_fn.__closure__]
    assert 99 in cell_contents


# ---------------------------------------------------------------------------
# 6. inspect.signature() — structured parameter introspection
# ---------------------------------------------------------------------------


def test_signature_represents_full_parameter_list() -> None:
    def func(a: int, b: str = "x", *, c: float) -> bool:  # noqa: ARG001
        return True

    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    assert param_names == ["a", "b", "c"]


def test_signature_parameter_kinds() -> None:
    def func(
        pos_only: int,
        /,
        regular: int,
        *args: int,
        kw_only: int,
        **kwargs: int,
    ) -> None:
        pass

    sig = inspect.signature(func)
    params = sig.parameters

    assert params["pos_only"].kind == inspect.Parameter.POSITIONAL_ONLY
    assert params["regular"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert params["args"].kind == inspect.Parameter.VAR_POSITIONAL
    assert params["kw_only"].kind == inspect.Parameter.KEYWORD_ONLY
    assert params["kwargs"].kind == inspect.Parameter.VAR_KEYWORD


def test_signature_shows_default_values() -> None:
    def func(x: int, y: int = 10) -> int:
        return x + y

    sig = inspect.signature(func)
    assert sig.parameters["y"].default == 10
    assert sig.parameters["x"].default is inspect.Parameter.empty


def test_signature_return_annotation() -> None:
    def add(x: int, y: int) -> int:
        return x + y

    sig = inspect.signature(add)
    assert sig.return_annotation is int


def test_signature_bind_maps_args_to_parameters() -> None:
    def func(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    bound = inspect.signature(func).bind(1, 2, c=3)
    bound.apply_defaults()
    assert dict(bound.arguments) == {"a": 1, "b": 2, "c": 3}


# ---------------------------------------------------------------------------
# 7. inspect.getsource() — retrieve source code as a string
# ---------------------------------------------------------------------------


def test_getsource_returns_function_source() -> None:
    def simple(x: int) -> int:
        return x * 2

    source = inspect.getsource(simple)
    assert "def simple" in source
    assert "return x * 2" in source


# ---------------------------------------------------------------------------
# 8. Detecting function kind
# ---------------------------------------------------------------------------


def test_isfunction_true_for_regular_functions() -> None:
    def f() -> None:
        pass

    assert inspect.isfunction(f)


def test_isfunction_false_for_builtins() -> None:
    # Built-in functions (implemented in C) are not Python functions
    assert not inspect.isfunction(len)
    assert inspect.isbuiltin(len)


def test_isgeneratorfunction_detects_yield() -> None:
    def gen() -> Generator[int]:
        yield 1

    def normal() -> int:
        return 1

    assert inspect.isgeneratorfunction(gen)
    assert not inspect.isgeneratorfunction(normal)


def test_iscoroutinefunction_detects_async_def() -> None:
    async def coro() -> None:
        pass

    def sync() -> None:
        pass

    assert inspect.iscoroutinefunction(coro)
    assert not inspect.iscoroutinefunction(sync)
