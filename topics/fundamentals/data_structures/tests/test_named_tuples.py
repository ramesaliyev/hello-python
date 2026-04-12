# Named tuples as pytest-verified learning notes.
# Covers: collections.namedtuple, typing.NamedTuple class syntax, and differences.


import collections
from typing import NamedTuple

import pytest

# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------

# collections.namedtuple — functional API
Point2D = collections.namedtuple("Point2D", ["x", "y"])  # noqa: PYI024 — teaching collections API
Color = collections.namedtuple("Color", "red green blue")  # noqa: PYI024 — space-separated string also works


# typing.NamedTuple — class-based API with type annotations
class Point3D(NamedTuple):
    x: float
    y: float
    z: float = 0.0  # default values are supported in typing.NamedTuple


class Employee(NamedTuple):
    name: str
    department: str
    salary: float


# ---------------------------------------------------------------------------
# 1. collections.namedtuple — field access
# ---------------------------------------------------------------------------


def test_namedtuple_field_access_by_name() -> None:
    p = Point2D(3, 4)
    assert p.x == 3
    assert p.y == 4


def test_namedtuple_field_access_by_index() -> None:
    # Named tuples are still tuples — integer indexing works
    p = Point2D(3, 4)
    assert p[0] == 3
    assert p[1] == 4


def test_namedtuple_is_a_tuple() -> None:
    p = Point2D(1, 2)
    assert isinstance(p, tuple)


def test_namedtuple_unpacking() -> None:
    p = Point2D(10, 20)
    x, y = p
    assert x == 10
    assert y == 20


# ---------------------------------------------------------------------------
# 2. Immutability
# ---------------------------------------------------------------------------


def test_namedtuple_is_immutable() -> None:
    p = Point2D(1, 2)
    with pytest.raises(AttributeError):
        p.x = 99  # type: ignore[misc]


def test_namedtuple_index_assignment_raises() -> None:
    p = Point2D(1, 2)
    with pytest.raises(TypeError):
        p[0] = 99  # type: ignore[index]


# ---------------------------------------------------------------------------
# 3. _replace(), _asdict(), _fields — the underscore-prefixed public API
# ---------------------------------------------------------------------------
# These methods use a leading underscore NOT to signal "private/internal" but
# to avoid colliding with user-defined field names. A namedtuple could have a
# field called `replace`, `fields`, or `asdict`, so the stdlib deliberately
# chose names that are unlikely to clash. This is standard practice and fully
# documented — treat them as stable public API.
# ---------------------------------------------------------------------------


def test_replace_returns_new_instance_with_changed_fields() -> None:
    p = Point2D(1, 2)
    new_p = p._replace(x=10)
    assert new_p == Point2D(10, 2)
    assert p == Point2D(1, 2)  # original is unchanged


def test_replace_multiple_fields() -> None:
    c = Color(255, 0, 0)
    grey = c._replace(green=128, blue=128)
    assert grey == Color(255, 128, 128)


# ---------------------------------------------------------------------------
# 4. _asdict() — convert to OrderedDict / dict
# ---------------------------------------------------------------------------


def test_asdict_returns_dict() -> None:
    p = Point2D(3, 4)
    d = p._asdict()
    assert d == {"x": 3, "y": 4}


def test_asdict_values_match_fields() -> None:
    emp = Employee("Alice", "Engineering", 90000.0)
    d = emp._asdict()
    assert d["name"] == "Alice"
    assert d["salary"] == 90000.0


# ---------------------------------------------------------------------------
# 5. _fields — introspect field names
# ---------------------------------------------------------------------------


def test_fields_returns_tuple_of_field_names() -> None:
    assert Point2D._fields == ("x", "y")
    assert Color._fields == ("red", "green", "blue")


def test_fields_useful_for_generic_processing() -> None:
    p = Point2D(3, 4)
    # Zip fields with values to build a dict generically
    mapping = dict(zip(Point2D._fields, p, strict=True))
    assert mapping == {"x": 3, "y": 4}


# ---------------------------------------------------------------------------
# 6. typing.NamedTuple — class syntax with type annotations
# ---------------------------------------------------------------------------


def test_typed_namedtuple_field_access() -> None:
    p = Point3D(1.0, 2.0, 3.0)
    assert p.x == 1.0
    assert p.z == 3.0


def test_typed_namedtuple_default_value() -> None:
    # Default values work in typing.NamedTuple — not supported in collections.namedtuple
    p = Point3D(1.0, 2.0)  # z defaults to 0.0
    assert p.z == 0.0


def test_typed_namedtuple_is_still_a_tuple() -> None:
    p = Point3D(1.0, 2.0, 3.0)
    assert isinstance(p, tuple)
    assert p[2] == 3.0


def test_typed_namedtuple_is_immutable() -> None:
    p = Point3D(1.0, 2.0, 3.0)
    with pytest.raises(AttributeError):
        p.x = 9.0  # type: ignore[misc]


def test_typed_namedtuple_replace_and_asdict() -> None:
    emp = Employee("Bob", "Finance", 75000.0)
    promoted = emp._replace(salary=85000.0)
    assert promoted.salary == 85000.0
    assert emp.salary == 75000.0  # original unchanged

    d = emp._asdict()
    assert d["department"] == "Finance"


# ---------------------------------------------------------------------------
# 7. Equality and hashing
# ---------------------------------------------------------------------------


def test_namedtuple_equality_compares_values() -> None:
    assert Point2D(1, 2) == Point2D(1, 2)


def test_namedtuple_equals_equivalent_plain_tuple() -> None:
    # Named tuples compare equal to plain tuples with the same values
    p = Point2D(1, 2)
    assert p == (1, 2)


def test_different_namedtuple_types_with_same_values_are_equal() -> None:
    # Equality is based on tuple values, not the named-tuple class
    OtherPoint = collections.namedtuple("OtherPoint", ["x", "y"])  # noqa: PYI024 — teaching collections.namedtuple API
    assert Point2D(1, 2) == OtherPoint(1, 2)  # type: ignore[comparison-overlap]


def test_namedtuple_is_hashable_and_usable_as_dict_key() -> None:
    p = Point2D(3, 4)
    d = {p: "origin-ish"}
    assert d[Point2D(3, 4)] == "origin-ish"
