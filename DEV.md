# Developer Guide

Everything you need to set up, run, and extend this repo.

---

## Prerequisites

Only one tool needs to be installed manually: **uv**.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via Homebrew
brew install uv
```

Python 3.14 is **not** required to install separately — uv downloads and manages it automatically when you run `uv sync`.

---

## Setup

```bash
git clone https://github.com/ramesaliyev/hello-python
cd hello-python

# Creates .venv, installs Python 3.14, installs all dependencies from uv.lock
uv sync

# Installs pre-commit hooks into .git/hooks (one-time per clone)
uv run install-hooks
```

After this, every `git commit` will automatically run the pre-commit hooks (see below).

---

## Commands

All commands use `uv run <script>`, which activates the virtual environment transparently.

| Command | What it does |
|---|---|
| `uv run test` | Run the full pytest suite with coverage. Generates an HTML report in `.coverage-report/`. |
| `uv run test-fast` | Run tests without coverage (`--no-cov`) and stop on the first failure (`-x`). Useful during active development. |
| `uv run lint` | Run ruff linter and report violations. |
| `uv run lint-fix` | Run ruff linter and auto-fix safe violations. |
| `uv run fmt` | Format all code with ruff (replaces black). |
| `uv run fmt-check` | Check formatting without modifying files. Exits non-zero if anything would change. |
| `uv run typecheck` | Run mypy over `topics/` and `src/`. |
| `uv run check` | Run lint → fmt-check → typecheck → test in sequence. Stops on first failure. |
| `uv run install-hooks` | Install pre-commit hooks (only needed once after cloning). |

These scripts are defined in `src/pylearn/_scripts.py` and registered under `[project.scripts]` in `pyproject.toml`.

---

## Pre-commit hooks

Hooks run automatically on every `git commit`. They are configured in `.pre-commit-config.yaml`.

### Hook groups

**1. General file hygiene** (`pre-commit/pre-commit-hooks`):
- `trailing-whitespace` — strips trailing spaces
- `end-of-file-fixer` — ensures files end with a single newline
- `check-yaml` / `check-toml` / `check-json` — validates config file syntax
- `check-merge-conflict` — blocks unresolved merge markers
- `debug-statements` — catches leftover `breakpoint()` / `pdb` calls
- `check-added-large-files` — blocks files > 500 KB

**2. Ruff** (`astral-sh/ruff-pre-commit`):
- `ruff --fix` — lints and auto-fixes safe violations
- `ruff-format` — formats code (equivalent to `uv run fmt`)

**3. mypy** (`pre-commit/mirrors-mypy`):
- Runs type checking with the config from `pyproject.toml`

### Skipping hooks (use sparingly)

```bash
git commit --no-verify -m "wip: skip hooks this once"
```

### Running hooks manually

```bash
# Run all hooks against all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff --all-files
```

---

## VS Code

### Required extension

Install the **Ruff** extension: `charliermarsh.ruff` (search "Ruff" in the Extensions panel).

### What happens automatically

The `.vscode/settings.json` is committed to the repo and configures:
- Python interpreter → `.venv/bin/python` (the uv-managed venv)
- Format on save → ruff formatter
- Fix all lint violations on save
- Organize imports on save
- Ruler at column 88 (matches `line-length = 88` in `pyproject.toml`)
- Trim trailing whitespace and insert final newlines

No manual configuration needed after installing the extension.

---

## CI pipeline

Defined in `.github/workflows/ci.yml`. Runs on every push to `master` and on every pull request targeting `master`.

### Steps (in order)

1. **Checkout** — fetch the repo
2. **Install uv** — pinned to `0.11.6` for reproducibility
3. **Install Python 3.14** — via uv
4. **`uv sync`** — install dependencies from `uv.lock`
5. **`uv run lint`** — ruff linter
6. **`uv run fmt-check`** — ruff formatter check
7. **`uv run typecheck`** — mypy
8. **`uv run test`** — pytest with coverage
9. **Upload coverage artifact** — HTML report available in the Actions run summary

All four quality gates must pass. Coverage report is uploaded even when tests fail.

---

## Project structure

```
hello-python/
├── src/
│   └── pylearn/
│       ├── __init__.py         # package marker
│       ├── _scripts.py         # dev scripts (uv run <command> entry points)
│       └── utils/
│           └── helpers.py      # shared test utilities (e.g. capture_stdout)
│
├── tests/
│   ├── __init__.py
│   └── conftest.py             # shared pytest fixtures
│
├── topics/                     # one subdirectory per learning topic
│   ├── basics/
│   │   ├── __init__.py
│   │   ├── *.py                # example/demo modules (also run as doctests)
│   │   └── tests/
│   │       └── test_*.py       # pytest tests for this topic
│   └── ...                     # same layout for every other topic
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
│
├── .vscode/
│   └── settings.json           # VS Code workspace settings (committed)
│
├── pyproject.toml              # project metadata, dependencies, tool configs
├── .pre-commit-config.yaml     # pre-commit hook definitions
├── .python-version             # Python version for uv (3.14)
├── uv.lock                     # locked dependency graph (committed)
├── .gitignore
├── README.md
└── DEV.md                      # this file
```

---

## Tool configuration

All tool configuration lives in `pyproject.toml`. Key sections:

| Section | Tool | Notes |
|---|---|---|
| `[tool.pytest.ini_options]` | pytest | testpaths, coverage, doctest, asyncio mode |
| `[tool.coverage.run]` | coverage.py | source dirs, omit patterns |
| `[tool.ruff]` | ruff | target Python, line length, source dirs |
| `[tool.ruff.lint]` | ruff linter | `select = ["ALL"]` with learning-friendly ignores |
| `[tool.ruff.format]` | ruff formatter | double quotes, space indent |
| `[tool.mypy]` | mypy | strict only for `topics/type_hints/*` |

---

## Type checking in detail

mypy runs in **strict mode only for `topics/type_hints/*`**. All other modules use lenient settings (no strict flags).

This is intentional: `topics/type_hints/` is the dedicated learning topic for Python type annotations. Enforcing strict mode across the whole repo would produce noisy errors in unrelated learning examples that aren't focused on types.

The configuration lives in `pyproject.toml` under `[tool.mypy]` as per-module overrides:

```toml
[tool.mypy]
# lenient defaults ...

[[tool.mypy.overrides]]
module = "topics.type_hints.*"
strict = true
```

---

## How to add a new topic

1. Create a directory under `topics/`:
   ```
   topics/<category>/your_topic/
   ├── __init__.py          # empty or a short module docstring
   ├── README.md            # link to test files and external resources
   └── tests/
       ├── __init__.py
       └── test_examples.py
   ```

2. Follow the naming convention for test files: `test_*.py`.

3. pytest discovers tests automatically — no registration needed.

4. **Maintain the README chain.** Every level from the root down must link to the new content:
   ```
   README.md → topics/README.md → topics/<category>/README.md → topics/<category>/your_topic/README.md
   ```
   Trace upward and add any missing entries or links at each level.

5. Run `uv run test-fast` to verify your new tests pass before committing.

6. Commit — pre-commit hooks will lint, format, and type-check your new files automatically.
