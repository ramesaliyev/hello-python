"""Development scripts — installed as project.scripts, run via: uv run <name>."""

import subprocess
import sys


def _run(*cmd: str) -> None:
    result = subprocess.run(list(cmd), check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def install_hooks() -> None:
    """Install pre-commit hooks."""
    _run("pre-commit", "install")


def test() -> None:
    """Run full test suite with coverage."""
    _run("pytest")


def test_fast() -> None:
    """Run tests without coverage, stop on first failure."""
    _run("pytest", "--no-cov", "-x")


def lint() -> None:
    """Run ruff linter."""
    _run("ruff", "check", ".")


def lint_fix() -> None:
    """Run ruff linter with auto-fix."""
    _run("ruff", "check", "--fix", ".")


def fmt() -> None:
    """Format code with ruff."""
    _run("ruff", "format", ".")


def fmt_check() -> None:
    """Check formatting without making changes."""
    _run("ruff", "format", "--check", ".")


def typecheck() -> None:
    """Run mypy type checker."""
    _run("mypy", "topics/", "src/")


def check() -> None:
    """Run all checks: lint, format check, type check, tests."""
    lint()
    fmt_check()
    typecheck()
    test()
