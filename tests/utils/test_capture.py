import sys

import pytest

from tests.utils.capture import capture_stdout


def test_capture_stdout_captures_print() -> None:
    with capture_stdout() as buf:
        print("hello")
    assert buf.getvalue() == "hello\n"


def test_capture_stdout_restores_stdout() -> None:
    original = sys.stdout
    with capture_stdout():
        pass
    assert sys.stdout is original


def test_capture_stdout_restores_stdout_on_exception() -> None:
    original = sys.stdout
    with pytest.raises(ValueError), capture_stdout():
        raise ValueError
    assert sys.stdout is original
