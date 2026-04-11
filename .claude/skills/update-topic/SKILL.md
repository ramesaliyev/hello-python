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
