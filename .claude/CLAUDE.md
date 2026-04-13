# CLAUDE.md

Guidelines for Claude Code working in this repository.

---

## Project Overview

A structured Python learning repository — basics to advanced.
**Python 3.14**, managed with **uv**, tests written as educational notes.

---

## Package Manager

Use `uv` exclusively. Never use pip or Poetry directly.

```bash
uv run test          # full pytest suite + coverage
uv run test-fast     # tests only, stop on first failure
uv run lint          # ruff lint
uv run lint-fix      # ruff lint + auto-fix
uv run fmt           # ruff format
uv run fmt-check     # format check (no writes)
uv run typecheck     # mypy
uv run check         # lint → fmt-check → typecheck → test
```

Scripts are defined in `src/dev/_scripts.py` and registered under `[project.scripts]` in `pyproject.toml`.

When adding a dependency, always web-search for its latest version and read the current documentation before using it.

---

## Repository Structure

```
topics/       # learning content — all pytest discovery happens here
src/dev/      # dev scripts and shared utilities (keep lean)
tests/        # cross-topic fixtures and utility tests
```

---

## Adding New Topics

Use the `/update-topic` skill — it contains the full procedure: directory layout, README chain rules, and link label format.

---

## Test Conventions

- Type-hint all test functions: `def test_foo() -> None:`
- `--doctest-modules` is active — doctests in `.py` files run automatically.
- Async tests work without decoration (`asyncio_mode = "auto"`).
- Available markers: `slow`, `integration`.

### Comments in tests

Add inline comments when the test covers behaviour the function name alone does not convey.
If the name is fully self-explanatory (e.g., `test_set_is_unordered`), comments are not required.

---

## Config File Documentation

Whenever you add or change a setting in any config file — `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.vscode/settings.json`, or any other — add an inline comment explaining:
- **what** the setting does
- **why** it is set this way (the reasoning, not just a restatement of the value)

This applies to new additions and to any section you touch while making other changes. The goal is that someone reading the file cold can understand every option without looking it up.

---

## Code Style

Tool: **Ruff** (lint + format).

- Line length: 88, double quotes.
- `print()` is allowed (T201/T203 suppressed — learning repo).
- Commented-out code is allowed (ERA001 suppressed).
- Pre-commit hooks run lint, format, and type-check automatically on every commit.
- Always use the latest Python conventions and modern language features appropriate for Python 3.14.

### Suppression comments (`# noqa` / `# type: ignore`)

- Use them **only** when the rule genuinely does not apply in context, or when the code intentionally violates best practice for a teaching reason.
- If unsure whether a suppression is warranted, **ask** rather than silently adding one.
- **Always include an inline reason** on the same line, separated by `—`:
  ```python
  {[1], 1}  # noqa: B018 — set literal is intentional to trigger TypeError
  ```
- Never suppress a rule just to make a warning go away; prefer fixing the code instead.
- **When combining `type: ignore` and `# noqa` on the same line, `type: ignore` must come first.**
  Placing it after `# noqa` embeds it inside the first comment's text where mypy cannot find it.
  ```python
  # Correct:
  assert 1 != 2  # type: ignore[comparison-overlap]  # noqa: PLR0133 — demonstrating !=
  # Wrong — mypy will not see the type: ignore:
  assert 1 != 2  # noqa: PLR0133 — demonstrating !=  # type: ignore[comparison-overlap]
  ```

---

## Test File Structure

Applies to all test files in the repo.

### Internal layout

```python
# One-line description of what this file covers.

import pytest  # only if needed

# ---------------------------------------------------------------------------
# Helpers shared across tests  (omit section if none)
# ---------------------------------------------------------------------------

class MyHelper: ...

# ---------------------------------------------------------------------------
# 1. First concept group
# ---------------------------------------------------------------------------

def test_something() -> None:
    ...

# ---------------------------------------------------------------------------
# 2. Second concept group
# ---------------------------------------------------------------------------
```

- **Group related tests** under numbered section headers.
- **Helpers** (dataclasses, enums, small classes) go at the top under their own header — never inline inside a test function unless the helper is specific to that one test.
- **Variable names**: use descriptive names (`filled_dict`, `our_iterator`) not single letters (`d`, `it`).

For teaching-specific lint suppressions and the lint-fix danger warning, see the `update-topic` skill.

---

## Type Checking (mypy)

mypy runs in **strict mode only for `topics/type_hints/*`**.
All other modules use lenient settings.

This is intentional: `topics/type_hints/` is the dedicated topic for learning type annotations.
Enabling strict mode everywhere would make unrelated learning examples unnecessarily noisy.

Configuration: `[tool.mypy]` in `pyproject.toml` with per-module overrides.

### Strict-mode leakage (important gotcha)

When `strict = true` is set in **any** per-module override, mypy treats the strict flags
(`disallow_untyped_defs`, `disallow_incomplete_defs`, `disallow_untyped_decorators`,
`disallow_untyped_calls`, `disallow_any_generics`, `warn_return_any`, …) as new **global
defaults** for the entire run, not just that module. Other modules inherit them unless a
second override explicitly resets each flag to `false`.

The test-module override in `pyproject.toml` exists precisely to counter this effect:

```toml
[[tool.mypy.overrides]]
module = ["topics.*.tests.*", "topics.*.*.tests.*"]
disallow_untyped_defs        = false
disallow_incomplete_defs     = false
disallow_untyped_decorators  = false
disallow_untyped_calls       = false
disallow_any_generics        = false
warn_return_any              = false
```

If new `[no-untyped-def]` / `[untyped-decorator]` / `[no-any-return]` errors appear in
test files that are supposed to be lenient, the likely cause is a new strict flag leaking
from the `topics.type_hints.*` override. Add the corresponding `= false` reset to the
test-module override.

---

## CI Pipeline

`.github/workflows/ci.yml` — triggers on push/PR to `master`.

1. Ruff lint check
2. Ruff format check
3. mypy type check
4. pytest + coverage

All four gates must pass.

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | All metadata, deps, and tool config |
| `DEV.md` | Full developer guide (setup, commands, conventions) |
| `.pre-commit-config.yaml` | Git hooks |
| `.github/workflows/ci.yml` | CI definition |
| `tests/utils/capture.py` | stdout capture utility for tests |
