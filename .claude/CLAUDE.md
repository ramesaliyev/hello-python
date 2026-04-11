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

Scripts are defined in `src/pylearn/_scripts.py` and registered under `[project.scripts]` in `pyproject.toml`.

When adding a dependency, always web-search for its latest version and read the current documentation before using it.

---

## Repository Structure

```
topics/       # learning content — all pytest discovery happens here
src/pylearn/  # shared utilities (keep lean)
tests/        # cross-topic fixtures and utility tests
```

---

## Adding New Topics — README Chain is Mandatory

Standard layout:

```
topics/<category>/<topic>/
├── __init__.py
├── README.md          ← required; link to test files and external resources
└── tests/
    ├── __init__.py
    └── test_<topic>.py
```

**Every time content is added, maintain the full README chain:**

```
README.md → topics/README.md → topics/<category>/README.md → topics/<category>/<topic>/README.md
```

Trace upward from the new file and add any missing links or entries at each level.
Topic READMEs must link to their test files and to relevant external resources.

### Test file link format

Link to test files using this exact format:

```markdown
- [subtopic name](tests/test_file.py) — optional description
```

- The **label** must be a human-readable subtopic name: lowercase words separated by spaces, no `test_` prefix, no underscores.
  - Correct: `[match case](tests/test_match_case.py)`
  - Wrong: `[test_match_case](tests/test_match_case.py)` or `` `tests/test_match_case.py` ``
- The **path** is relative from the topic README to the test file (always `tests/test_*.py`).

---

## Test Conventions

- Type-hint all test functions: `def test_foo() -> None:`
- `--doctest-modules` is active — doctests in `.py` files run automatically.
- Async tests work without decoration (`asyncio_mode = "auto"`).
- Available markers: `slow`, `integration`.

### Comments in learning tests

Add inline comments when the test covers behaviour the function name alone does not convey.
If the name is fully self-explanatory (e.g., `test_set_is_unordered`), comments are not required.

### Content of learning tests

- Always include tricky edge cases and important "must-know" behaviours — not just the happy path.
- If asked to add "everything" or make tests "comprehensive", do a web search first to find current best practices and surprising gotchas for that topic.

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

---

## Type Checking (mypy)

mypy runs in **strict mode only for `topics/type_hints/*`**.
All other modules use lenient settings.

This is intentional: `topics/type_hints/` is the dedicated topic for learning type annotations.
Enabling strict mode everywhere would make unrelated learning examples unnecessarily noisy.

Configuration: `[tool.mypy]` in `pyproject.toml` with per-module overrides.

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
