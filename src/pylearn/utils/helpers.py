"""General-purpose helpers used across tutorial files and tests."""

from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO
import sys


@contextmanager
def capture_stdout() -> Generator[StringIO]:
    """Context manager that captures everything written to stdout.

    Useful for testing functions that use print().

    Example::

        with capture_stdout() as buf:
            print("hello")
        assert buf.getvalue() == "hello\\n"
    """
    old = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        yield buf
    finally:
        sys.stdout = old
