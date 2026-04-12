---
name: update-topic
description: Apply whenever working inside the topics/ folder — adding a new topic, adding tests to an existing topic, or any other change under topics/. Covers directory layout (new topics), README chain maintenance, and link label format rules.
---

## Test Content

- Always include tricky edge cases and important "must-know" behaviours — not just the happy path.
- If asked to add "everything" or make tests "comprehensive", do a web search first to find current best practices and surprising gotchas for that topic.

### Beyond mechanics — teach the full picture

Tests **must** cover mechanics thoroughly. They should *also* cover:

- **Why it's useful** — what problem this feature solves, and when to reach for it over alternatives. A test named `test_generator_is_more_memory_efficient_than_list` adds value on top of `test_generator_basic`.
- **Practical usage patterns** — idioms and real-world scenarios. Show the feature doing something meaningful alongside the toy examples that explain the mechanics.
- **What to avoid / antipatterns** — common mistakes, surprising gotchas, and subtle behaviour that burns people in practice. These are often the most valuable tests in a topic.

Group these naturally within the relevant section, or add a dedicated "Pitfalls" section at the end of the file for mistakes that span multiple mechanics.

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

## README Resources — Mandatory

Every topic README with actual content **must** have a `## Resources` section.

### What to include

- **Python official docs** for every concept covered — link to the most specific page (e.g. `docs.python.org/3/library/contextlib.html` rather than just the top-level docs).
- **PEPs** for any language feature that was introduced or significantly changed by a PEP.
- **Real Python articles** (`realpython.com`) when a thorough, well-regarded article exists for the topic.
- Other quality articles only if they add genuine value beyond the above.

### Where to find them

- Python official docs: `https://docs.python.org/3/` — use the tutorial, library reference, or language reference as appropriate.
- PEPs: `https://peps.python.org/pep-XXXX/`
- Real Python: `https://realpython.com/` — do a web search to confirm the article exists and covers the right topic.

### Ordering

List resources in this order:
1. Python Docs links (most specific first)
2. PEP links (chronological)
3. Real Python articles
4. Other articles / general references (e.g. Learn X in Y Minutes)

### Example

```markdown
## Resources

- [Python Docs — contextlib](https://docs.python.org/3/library/contextlib.html)
- [Python Docs — Async Context Managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
- [PEP 343 — The with Statement](https://peps.python.org/pep-0343/)
- [Real Python — Context Managers and the `with` Statement](https://realpython.com/python-with-statement/)
```

---

## Writing Test Files

> Python 3.14 is the language standard. Reach for modern idioms first — prefer match/case, walrus, ExceptionGroup, etc. Consult the `/python-practices` skill for the full prescriptive list.

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
