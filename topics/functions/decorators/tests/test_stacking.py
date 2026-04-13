# Decorator stacking: application order, execution order, and order-dependent behaviour.


# ---------------------------------------------------------------------------
# 1. Application order — bottom-up
# ---------------------------------------------------------------------------


def test_decorators_apply_bottom_up_inner_decorator_wraps_first() -> None:
    # Given:
    #   @outer
    #   @inner
    #   def func(): ...
    #
    # Python desugars this as: func = outer(inner(func))
    # So `inner` wraps `func` first, then `outer` wraps the result.
    applied: list[str] = []

    def make_decorator(name: str):
        def decorator(func):
            applied.append(name)

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @make_decorator("outer")
    @make_decorator("inner")
    def greet() -> str:
        return "hello"

    assert applied == ["inner", "outer"]


def test_stacking_desugars_to_nested_calls() -> None:
    # @c      is equivalent to: func = c(b(a(func)))
    # @b
    # @a
    # def func(): ...
    def add_char(char: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return char + func(*args, **kwargs)

            return wrapper

        return decorator

    @add_char("C")
    @add_char("B")
    @add_char("A")
    def base() -> str:
        return "x"

    # A wraps base first → "Ax", B wraps that → "BAx", C wraps that → "CBAx"
    assert base() == "CBAx"


# ---------------------------------------------------------------------------
# 2. Execution order — outermost wrapper first at call time
# ---------------------------------------------------------------------------


def test_stacked_decorators_execute_outermost_first_at_call_time() -> None:
    # Application is bottom-up, but execution at call time is top-down:
    # the outermost wrapper runs first, then calls inward.
    log: list[str] = []

    def make_logging_decorator(name: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                log.append(f"{name}:enter")
                result = func(*args, **kwargs)
                log.append(f"{name}:exit")
                return result

            return wrapper

        return decorator

    @make_logging_decorator("outer")
    @make_logging_decorator("inner")
    def work() -> None:
        log.append("work")

    work()

    assert log == [
        "outer:enter",
        "inner:enter",
        "work",
        "inner:exit",
        "outer:exit",
    ]


def test_stacking_wraps_like_concentric_shells() -> None:
    # Each wrapper is one shell further out. The call enters the outermost
    # shell first and exits it last — like peeling an onion in reverse.
    depths: list[int] = []
    depth = {"current": 0}

    def track_depth(func):
        def wrapper(*args, **kwargs):
            depth["current"] += 1
            depths.append(depth["current"])
            result = func(*args, **kwargs)
            depth["current"] -= 1
            return result

        return wrapper

    @track_depth
    @track_depth
    @track_depth
    def core() -> None:
        depths.append(depth["current"])

    core()
    # Three wrappers enter at depths 1, 2, 3; core also sees depth 3
    assert depths == [1, 2, 3, 3]


# ---------------------------------------------------------------------------
# 3. Gotcha: order matters — swapping decorators changes behaviour
# ---------------------------------------------------------------------------


def test_decorator_order_determines_which_transformation_runs_first() -> None:
    def add_ten(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) + 10

        return wrapper

    def double(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) * 2

        return wrapper

    @add_ten  # outer — runs last on the result
    @double  # inner — runs first on the result
    def value_v1() -> int:
        return 5  # double → 10, add_ten → 20

    @double  # outer — runs last
    @add_ten  # inner — runs first
    def value_v2() -> int:
        return 5  # add_ten → 15, double → 30

    assert value_v1() == 20
    assert value_v2() == 30


def test_order_matters_for_caching_combined_with_validation() -> None:
    # Cache outside validator: on repeated calls the cache short-circuits and
    # validation is skipped — valid inputs are cached as intended, but the
    # second call saves a validation round-trip.
    validation_runs: list[int] = []
    call_cache: dict[int, int] = {}

    def validate_positive(func):
        def wrapper(n: int) -> int:
            validation_runs.append(n)
            if n < 0:
                raise ValueError(f"must be positive: {n}")
            return func(n)

        return wrapper

    def simple_cache(func):
        def wrapper(n: int) -> int:
            if n not in call_cache:
                call_cache[n] = func(n)
            return call_cache[n]

        return wrapper

    @simple_cache  # outer — checked first; bypasses inner on cache hit
    @validate_positive  # inner — only reached on cache miss
    def compute(n: int) -> int:
        return n * n

    compute(4)  # miss: runs validation → computes → caches
    compute(4)  # hit: cache returns directly, validation is skipped
    assert validation_runs == [4]  # validated only once


def test_order_matters_for_logging_combined_with_authentication() -> None:
    # Logging outermost: every request is logged, including denied ones.
    # Logging innermost: only requests that pass auth are logged.
    access_log: list[str] = []
    denied_log: list[str] = []

    def log_access(func):
        def wrapper(user: str) -> str | None:
            access_log.append(user)
            return func(user)

        return wrapper

    def require_auth(func):
        def wrapper(user: str) -> str | None:
            if user != "admin":
                denied_log.append(user)
                return None
            return func(user)

        return wrapper

    @log_access  # outer — sees every call
    @require_auth  # inner — rejects non-admins before reaching the function
    def secret_data(user: str) -> str:
        return f"secret for {user}"

    secret_data("admin")
    secret_data("attacker")

    assert access_log == ["admin", "attacker"]  # all attempts logged
    assert denied_log == ["attacker"]  # only rejections in denied_log
