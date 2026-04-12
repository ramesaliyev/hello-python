---
name: update-topic
description: Apply whenever working inside the topics/ folder — adding a new topic, adding tests to an existing topic, or any other change under topics/. Covers directory layout (new topics), README chain maintenance, and link label format rules.
---

## Test Content

- Always include tricky edge cases and important "must-know" behaviours — not just the happy path.
- If asked to add "everything" or make tests "comprehensive", do a web search first to find current best practices and surprising gotchas for that topic.

## Standard Layout

Every new topic must follow this structure:

```
topics/<category>/<topic>/
├── __init__.py
├── README.md          ← required; link to test files and external resources
└── tests/
    ├── __init__.py
    └── test_<topic>.py
```

## README Chain — Mandatory

**Every time content is added, maintain the full README chain:**

```
README.md → topics/README.md → topics/<category>/README.md → topics/<category>/<topic>/README.md
```

Trace upward from the new file and add any missing links or entries at each level.
Topic READMEs must link to their test files and to relevant external resources.

## Link Label Format

This rule applies to **all** links in README files — links to test files, to topic READMEs, and to any other file.

```markdown
- [subtopic name](tests/test_file.py) — optional description
- [control flow](fundamentals/control_flow/README.md) — optional description
```

- The **label** must be human-readable: lowercase words separated by spaces, no underscores, no `test_` prefix.
  - Correct: `[control flow](...)`, `[match case](...)`
  - Wrong: `[control_flow](...)`, `[test_match_case](...)`, `` `tests/test_match_case.py` ``
- The **path** is relative from the README containing the link.

## Writing Test Files

### Teaching tests and lint

**Never run `uv run lint-fix` on test files that intentionally demonstrate language behaviour.** The auto-fixer will corrupt teaching examples silently:

- `type(42) is int` → `int is int` (UP003 — loses the entire point)
- `elif` chains → flat `if` chains (RET505 — removes what's being taught)
- `while/else` and `for/else` blocks silently removed (PLW0120)

Instead, add `# noqa: RULE — reason` suppressions by hand to preserve intent.

### Common teaching suppressions

These rules fire intentionally in educational tests. Use `# noqa: RULE — reason`:

| Rule | When it fires | Example reason |
|------|--------------|----------------|
| `UP003` | `type(x) is T` — teaching `type()` explicitly | `teaching type() usage` |
| `PLR0133` | Comparing two literals | `demonstrating != on literals` |
| `SIM222` / `SIM223` | `x or y` / `x and y` return-value demos | `demonstrating or's return value` |
| `PERF401` / `PERF402` | Intentional loop + append form | `showing loop form explicitly` |
| `RET505` | `elif` chain being taught | `teaching elif chain explicitly` |
| `PLW0120` | `while/else` or `for/else` being taught | `teaching while/else` |
| `C405`–`C410` | Constructor call form being taught (`list([...])`, `dict(...)`) | `teaching list() from tuple` |
| `FBT003` | `True`/`False` as intentional subjects | `True is intentional subject here` |
| `PYI024` | `collections.namedtuple` API being taught | `teaching collections API` |
| `SIM108` | `if/else` block form being taught (not ternary) | `teaching if/else form explicitly` |

Common `type: ignore` error codes in teaching tests:

| Code | Situation |
|------|-----------|
| `comparison-overlap` | Literal comparisons that can never be equal |
| `call-overload` | Tuple index on a list (`lst[1, 2]`) |
| `attr-defined` | Attribute access on a union type containing `object` |
| `misc` | Assignment to a namedtuple or other immutable field |
