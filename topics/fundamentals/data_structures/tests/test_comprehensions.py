# Comprehension syntax as pytest-verified learning notes.
# Covers: list, dict, set comprehensions, nesting, conditionals, and scope behaviour.


# ---------------------------------------------------------------------------
# 1. List comprehensions
# ---------------------------------------------------------------------------


def test_list_comprehension_basic() -> None:
    squares = [x**2 for x in range(5)]
    assert squares == [0, 1, 4, 9, 16]


def test_list_comprehension_with_filter() -> None:
    evens = [x for x in range(10) if x % 2 == 0]
    assert evens == [0, 2, 4, 6, 8]


def test_list_comprehension_with_transformation_and_filter() -> None:
    result = [x**2 for x in range(10) if x % 2 == 0]
    assert result == [0, 4, 16, 36, 64]


def test_list_comprehension_equals_equivalent_loop() -> None:
    # Comprehension and explicit loop must produce identical results
    data = [3, 1, 4, 1, 5, 9, 2, 6]

    via_loop: list[int] = []
    for x in data:
        if x > 3:
            via_loop.append(x * 2)  # noqa: PERF401 — intentional: showing the loop equivalent

    via_comp = [x * 2 for x in data if x > 3]
    assert via_comp == via_loop


def test_list_comprehension_over_string() -> None:
    vowels = [ch for ch in "hello world" if ch in "aeiou"]
    assert vowels == ["e", "o", "o"]


# ---------------------------------------------------------------------------
# 2. Dict comprehensions
# ---------------------------------------------------------------------------


def test_dict_comprehension_basic() -> None:
    squares = {x: x**2 for x in range(5)}
    assert squares == {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}


def test_dict_comprehension_with_filter() -> None:
    even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
    assert even_squares == {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}


def test_dict_comprehension_invert_mapping() -> None:
    original = {"a": 1, "b": 2, "c": 3}
    inverted = {v: k for k, v in original.items()}
    assert inverted == {1: "a", 2: "b", 3: "c"}


def test_dict_comprehension_from_two_lists() -> None:
    keys = ["name", "age", "city"]
    values = ["Alice", 30, "Istanbul"]
    result = {k: v for k, v in zip(keys, values, strict=True)}  # noqa: C416 — teaching dict comp syntax; dict(zip(...)) is the idiomatic alternative
    assert result == {"name": "Alice", "age": 30, "city": "Istanbul"}


def test_dict_comprehension_duplicate_keys_last_wins() -> None:
    # When keys collide, the last value processed overwrites earlier ones
    pairs = [("a", 1), ("b", 2), ("a", 3)]
    result = {k: v for k, v in pairs}  # noqa: C416 — teaching dict comp syntax
    assert result == {"a": 3, "b": 2}


# ---------------------------------------------------------------------------
# 3. Set comprehensions
# ---------------------------------------------------------------------------


def test_set_comprehension_basic() -> None:
    squares = {x**2 for x in range(5)}
    assert squares == {0, 1, 4, 9, 16}


def test_set_comprehension_deduplicates() -> None:
    # Sets cannot hold duplicates — repeated values collapse
    result = {x % 3 for x in range(9)}
    assert result == {0, 1, 2}


def test_set_comprehension_with_filter() -> None:
    odd = {x for x in range(10) if x % 2 != 0}
    assert odd == {1, 3, 5, 7, 9}


# ---------------------------------------------------------------------------
# 4. Nested comprehensions
# ---------------------------------------------------------------------------


def test_nested_list_comprehension_matrix_flatten() -> None:
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    flat = [cell for row in matrix for cell in row]
    assert flat == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_nested_list_comprehension_cartesian_product() -> None:
    # Two for clauses produce all combinations
    result = [(x, y) for x in [1, 2] for y in ["a", "b"]]
    assert result == [(1, "a"), (1, "b"), (2, "a"), (2, "b")]


def test_nested_comprehension_for_clause_order() -> None:
    # The for clauses read left-to-right, just like nested loops
    outer_first: list[tuple[int, int]] = []
    for i in range(3):
        for j in range(3):
            outer_first.append((i, j))  # noqa: PERF401 — intentional: showing the loop equivalent

    via_comp = [(i, j) for i in range(3) for j in range(3)]
    assert via_comp == outer_first


def test_nested_comprehension_build_matrix() -> None:
    # Inner list comprehension creates each row
    matrix = [[row * col for col in range(1, 4)] for row in range(1, 4)]
    assert matrix == [[1, 2, 3], [2, 4, 6], [3, 6, 9]]


# ---------------------------------------------------------------------------
# 5. Conditional expression inside comprehension (ternary in output)
# ---------------------------------------------------------------------------


def test_ternary_in_comprehension_output() -> None:
    # `x if cond else y` transforms the value; the `if` after `for` filters
    result = ["even" if x % 2 == 0 else "odd" for x in range(5)]
    assert result == ["even", "odd", "even", "odd", "even"]


def test_ternary_vs_filter_difference() -> None:
    data = range(6)
    # filter: only include evens — shorter list
    filtered = [x for x in data if x % 2 == 0]
    # ternary: replace every element — same length as input
    replaced = [x if x % 2 == 0 else -1 for x in data]
    assert filtered == [0, 2, 4]
    assert replaced == [0, -1, 2, -1, 4, -1]
    assert len(replaced) == len(list(data))


def test_ternary_clamp_values() -> None:
    data = [-2, 0, 3, 7, 10, 15]
    clamped = [max(0, min(x, 10)) for x in data]
    assert clamped == [0, 0, 3, 7, 10, 10]


# ---------------------------------------------------------------------------
# 6. Scope — comprehension variables do not leak (Python 3)
# ---------------------------------------------------------------------------


def test_list_comprehension_variable_does_not_leak() -> None:
    # In Python 3, the loop variable is local to the comprehension
    x = "outer"
    result = [x * 2 for x in range(3)]  # noqa: F841 — result used implicitly
    assert x == "outer"  # the outer x is unaffected


def test_walrus_operator_does_leak_from_comprehension() -> None:
    # := (walrus) is an exception: it leaks the variable into the enclosing scope
    last = -1
    _ = [last := n for n in range(5)]
    assert last == 4  # walrus leaked the final value


def test_nested_comprehension_inner_variable_is_local() -> None:
    j = "outer"
    _ = [(i, j) for i in range(2) for j in range(2)]
    assert j == "outer"  # inner j does not overwrite the outer j
