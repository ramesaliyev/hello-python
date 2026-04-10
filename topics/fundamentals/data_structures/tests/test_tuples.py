# Tuple unpacking examples as pytest-verified learning notes.


def test_basic_unpacking() -> None:
    a, b, c = (1, 2, 3)
    assert a == 1
    assert b == 2
    assert c == 3


def test_extended_unpacking() -> None:
    # *b captures everything between the first and last elements
    a, *b, c = (1, 2, 3, 4)
    assert a == 1
    assert b == [2, 3]
    assert c == 4


def test_implicit_tuple_unpacking() -> None:
    # Parentheses are optional — bare comma creates a tuple
    d, e, f = 4, 5, 6
    assert d == 4
    assert e == 5
    assert f == 6


def test_swap_via_unpacking() -> None:
    d, e = 4, 5
    e, d = d, e  # swap without a temp variable
    assert d == 5
    assert e == 4
