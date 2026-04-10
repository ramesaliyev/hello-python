"""Shared pytest fixtures for src/ tests."""

from collections.abc import Generator
from io import StringIO

import pytest

from pylearn.utils.helpers import capture_stdout as _capture_stdout


@pytest.fixture
def capture_stdout() -> Generator[StringIO]:
    with _capture_stdout() as buf:
        yield buf
