# Loop constructs as pytest-verified learning notes.
# Covers: for, while, break, continue, else clause, nested loops, range() variations.


# ---------------------------------------------------------------------------
# 1. for loop — iterating sequences and iterables
# ---------------------------------------------------------------------------


def test_for_loop_over_list() -> None:
    total = 0
    for n in [1, 2, 3, 4]:
        total += n
    assert total == 10


def test_for_loop_over_string() -> None:
    # Iterating a string yields individual characters
    chars: list[str] = []
    for ch in "abc":
        chars.append(ch)  # noqa: PERF402 — teaching the loop form explicitly
    assert chars == ["a", "b", "c"]


def test_for_loop_over_dict_iterates_keys() -> None:
    d = {"x": 1, "y": 2}
    keys: list[str] = []
    for k in d:
        keys.append(k)  # noqa: PERF402 — teaching the loop form explicitly
    assert keys == ["x", "y"]


def test_for_loop_with_items() -> None:
    d = {"a": 1, "b": 2}
    pairs: list[tuple[str, int]] = []
    for k, v in d.items():
        pairs.append((k, v))
    assert pairs == [("a", 1), ("b", 2)]


def test_for_loop_with_enumerate() -> None:
    result: list[tuple[int, str]] = []
    for i, ch in enumerate("xy"):
        result.append((i, ch))
    assert result == [(0, "x"), (1, "y")]


def test_for_loop_with_tuple_unpacking() -> None:
    pairs = [(1, "one"), (2, "two")]
    numbers: list[int] = []
    words: list[str] = []
    for num, word in pairs:
        numbers.append(num)
        words.append(word)
    assert numbers == [1, 2]
    assert words == ["one", "two"]


# ---------------------------------------------------------------------------
# 2. while loop
# ---------------------------------------------------------------------------


def test_while_runs_until_condition_false() -> None:
    count = 0
    while count < 3:
        count += 1
    assert count == 3


def test_while_body_skipped_when_condition_initially_false() -> None:
    count = 0
    while False:
        count += 1
    assert count == 0


def test_while_with_sentinel_value() -> None:
    data = [1, 2, 3, 0, 4]
    index = 0
    collected: list[int] = []
    while data[index] != 0:
        collected.append(data[index])
        index += 1
    assert collected == [1, 2, 3]


# ---------------------------------------------------------------------------
# 3. break — exit the loop immediately
# ---------------------------------------------------------------------------


def test_break_exits_for_loop() -> None:
    found: int | None = None
    for n in [10, 20, 30, 40]:
        if n == 30:
            found = n
            break
    assert found == 30


def test_break_stops_before_end() -> None:
    visited: list[int] = []
    for n in [1, 2, 3, 4, 5]:
        if n == 3:
            break
        visited.append(n)
    assert visited == [1, 2]


def test_break_exits_while_loop() -> None:
    count = 0
    while True:
        count += 1
        if count == 5:
            break
    assert count == 5


# ---------------------------------------------------------------------------
# 4. continue — skip the rest of this iteration
# ---------------------------------------------------------------------------


def test_continue_skips_current_iteration() -> None:
    evens: list[int] = []
    for n in range(6):
        if n % 2 != 0:
            continue
        evens.append(n)
    assert evens == [0, 2, 4]


def test_continue_in_while() -> None:
    total = 0
    n = 0
    while n < 5:
        n += 1
        if n == 3:
            continue  # skip adding 3
        total += n
    assert total == 1 + 2 + 4 + 5  # 3 was skipped


# ---------------------------------------------------------------------------
# 5. else clause on loops — runs when loop completes without break
# ---------------------------------------------------------------------------


def test_for_else_runs_when_no_break() -> None:
    # The else block executes after the for loop exhausts normally
    result = "not found"
    for n in [1, 2, 3]:
        if n == 99:
            result = "found"
            break
    else:
        result = "exhausted"
    assert result == "exhausted"


def test_for_else_skipped_when_break_taken() -> None:
    # The else block is skipped if a break was hit
    result = "not set"
    for n in [1, 2, 3]:
        if n == 2:
            result = "broke"
            break
    else:
        result = "exhausted"
    assert result == "broke"


def test_while_else_runs_when_condition_becomes_false() -> None:
    count = 0
    while count < 3:
        count += 1
    else:  # noqa: PLW0120 — teaching while/else; else runs when condition goes false
        result = "done"
    assert result == "done"


def test_while_else_skipped_on_break() -> None:
    count = 0
    result = "not set"
    while count < 10:
        count += 1
        if count == 3:
            result = "broke"
            break
    else:
        result = "exhausted"
    assert result == "broke"


def test_for_else_useful_for_search() -> None:
    # Classic use: scan a list; if the item isn't found, the else branch handles it
    def find_even(numbers: list[int]) -> str:
        for n in numbers:
            if n % 2 == 0:
                return f"found {n}"
        else:  # noqa: PLW0120 — teaching for/else; break is inside `return`, not explicit
            return "none found"

    assert find_even([1, 3, 4, 5]) == "found 4"
    assert find_even([1, 3, 5]) == "none found"


# ---------------------------------------------------------------------------
# 6. Nested loops — break only exits the innermost loop
# ---------------------------------------------------------------------------


def test_nested_for_loops() -> None:
    pairs: list[tuple[int, int]] = []
    for i in range(1, 3):
        for j in range(1, 3):
            pairs.append((i, j))  # noqa: PERF401 — teaching nested loop form explicitly
    assert pairs == [(1, 1), (1, 2), (2, 1), (2, 2)]


def test_break_in_inner_loop_does_not_affect_outer() -> None:
    outer_iterations: list[int] = []
    for i in range(3):
        outer_iterations.append(i)
        for j in range(5):
            if j == 1:
                break  # only exits inner loop
    # outer loop ran all 3 iterations
    assert outer_iterations == [0, 1, 2]


def test_flag_pattern_to_break_outer_loop() -> None:
    # Python has no labeled break; use a flag variable to break out of nested loops
    found: tuple[int, int] | None = None
    stop = False
    for i in range(5):
        for j in range(5):
            if i + j == 6:
                found = (i, j)
                stop = True
                break
        if stop:
            break
    assert found == (2, 4)


# ---------------------------------------------------------------------------
# 7. range() in loop contexts
# ---------------------------------------------------------------------------


def test_range_as_loop_counter() -> None:
    result: list[int] = []
    for i in range(5):
        result.append(i)  # noqa: PERF402 — teaching loop + append form explicitly
    assert result == [0, 1, 2, 3, 4]


def test_range_with_start_and_stop() -> None:
    result = list(range(2, 7))
    assert result == [2, 3, 4, 5, 6]


def test_range_with_step() -> None:
    result = list(range(0, 10, 3))
    assert result == [0, 3, 6, 9]


def test_range_countdown() -> None:
    result = list(range(5, 0, -1))
    assert result == [5, 4, 3, 2, 1]


def test_loop_variable_after_for() -> None:
    # The loop variable retains its last value after the loop finishes
    for last in range(5):  # noqa: B007 — `last` is intentionally read after the loop
        pass
    assert last == 4
