---
name: python-practices
description: Apply whenever writing or reviewing Python code — prescriptive best practices for Python 3.14: which idioms to prefer, which anti-patterns to avoid, and which modern language features to reach for first.
---

## Language Standard

Python 3.14 is the target. Always prefer the most modern idiomatic form available in 3.14.
When unsure about current best practice for a topic, web-search before writing.

## Living Document

When you discuss, teach, or implement a Python pattern that reveals a best practice not yet listed here, add it to the appropriate section before the conversation ends.

---

## 1. Types & Truthiness

- Use `isinstance()` over `type()` for type checks — respects inheritance and subclasses
- Use `is None` / `is not None`, never `== None`
- Prefer truthiness checks: `if items:` not `if len(items) > 0:`; `if not items:` not `if len(items) == 0:`
- Use `x or default` for falsy-fallback values (understand short-circuit: returns first truthy or last value)
- Use `is` only for singletons: `None`, `True`, `False`

## 2. Modern Syntax

- **Walrus operator `:=`** (3.8+) — assign inside expressions to avoid double evaluation:
  `if (n := len(data)) > 10:` or `while chunk := f.read(8192):`
- **Match/case structural pattern matching** (3.10+) — prefer over long if/elif chains for multi-way dispatch on type or structure; use:
  - Guard clauses: `case x if x > 0:`
  - Sequence patterns: `case [first, *rest]:`
  - Mapping patterns: `case {"type": "click", "pos": pos}:`
  - Class patterns: `case Point(x=0, y=0):`
  - `as` patterns: `case [_, *_] as full_list:`
  - Dotted-name value patterns (not captures): `case Color.RED:`
  - Catch-all: `case _:`
- **`zip(..., strict=True)`** (3.10+) — always use when zipping sequences that must be equal length
- **`dict | other`** / **`|=`** merging (3.9+) — prefer over `{**a, **b}` unless interleaving inline keys
- **`ExceptionGroup` + `except*`** (3.11+) — use for concurrent/async error aggregation where multiple independent exceptions occur
- **Chained comparisons** — `1 < x < 10` instead of `x > 1 and x < 10`; `x` is evaluated only once

## 3. Data Structures

- **`collections.Counter`** — for counting hashable items; missing keys return 0 (not KeyError); use `.most_common(n)`, and arithmetic operators (`+` adds, `-` subtracts dropping negatives, `&` keeps minimum, `|` keeps maximum)
- **`collections.defaultdict`** — for auto-initializing missing keys (`defaultdict(list)`, `defaultdict(int)`); prefer over manual `setdefault` loops
- **`typing.NamedTuple`** class syntax — prefer over `collections.namedtuple`; supports defaults and type annotations; use `_replace()` for modified copies, `_asdict()` for dict conversion
- **`dict.get(key, default)`** — prefer over `if key in d: ... d[key]`
- **`dict.pop(key, None)`** — prefer over check-then-delete
- **`dict.setdefault(key, val)`** — inserts only if key absent; never overwrites
- Tuple as dict key — for composite keys; lists are not hashable
- Lists as stacks — `append()`/`pop()` is O(1); use `collections.deque` for queues (`pop(0)` is O(n))
- Avoid `[[0]*n]*m` — all rows share the same list object; use `[[0]*n for _ in range(m)]`
- Dict views (`d.keys()`, `d.values()`, `d.items()`) are live — they reflect later mutations

## 4. Iteration

- **`enumerate(iterable, start=N)`** — always prefer over manual index tracking
- **`zip()`** — for parallel iteration; **`zip(*pairs)`** for unzipping / transposing
- **`any()`** / **`all()`** — short-circuit boolean queries; `any([]) == False`, `all([]) == True` (vacuous truth)
- **`next(iterator, default)`** — use the default to avoid `StopIteration`
- **Generator expressions** over `map()`/`filter()` — equally lazy, more readable; use `map`/`filter` only when directly passing to higher-order functions

## 5. Comprehensions

- Prefer comprehensions over explicit loops for transformations
- Filter form: `[x for x in items if cond]` — shorter list
- Ternary form: `[x if cond else y for x in items]` — same length, transformed values (these are different, don't confuse them)
- Flatten with nested comprehension: `[cell for row in matrix for cell in row]`
- Invert a mapping: `{v: k for k, v in d.items()}`
- Comprehension variables do **not** leak into enclosing scope (Python 3); walrus `:=` is the exception — it leaks

## 6. Functions

- **Mutable default arguments** — always use `None` sentinel, construct inside: `def f(items=None): items = [] if items is None else items`; default objects are shared across all calls
- **Keyword-only arguments (`*`)** — use `def f(a, *, b):` to force callers to name `b`; good for Boolean flags and optional config
- **Positional-only arguments (`/`)** — use `def f(a, /):` to prevent callers from using keyword form; good for library APIs
- **`functools.singledispatch`** — for type-based dispatch; register implementations per type, decouples type-specific logic from the base function
- **`functools.partial()`** — for specializing callables without writing wrapper functions
- **`operator.itemgetter()`** / **`attrgetter()`** / **`methodcaller()`** — prefer over lambdas as key/sort functions
- **Avoid assigning lambdas to variables** — use `def` instead; lambdas show `<lambda>` in tracebacks
- **`for/else`** — `else` runs when loop completes without `break`; idiomatic "search found nothing" pattern, no flag variable needed
- **`functools.reduce()`** — for cumulative operations with an initial value; supply `initial` argument to handle empty sequences

## 7. Error Handling

- Always catch specific exception types; never bare `except:` (catches `SystemExit`, `KeyboardInterrupt`, etc.)
- `except (ValueError, TypeError):` — multiple types in one clause
- **`try/except/else/finally`** — put "only-if-no-exception" code in `else`, not after the `try` block
- **Bare `raise`** inside `except` re-raises preserving the original traceback; `raise e` adds an extra frame
- **`raise NewError(...) from original`** — explicit exception chaining; sets `__cause__`; never silently drop the original with `raise NewError() from None` unless intentional
- **Inherit custom exceptions from `Exception`**, not `BaseException`; add custom attributes for structured error context
- **`contextlib.suppress(ExcType)`** — prefer over `try: ... except ExcType: pass`
- **`ExceptionGroup` / `except*`** (3.11+) — for multiple simultaneous errors (e.g., `asyncio.TaskGroup`)

## 8. Strings

- **f-strings** for all string formatting (3.6+); avoid legacy `%` formatting and `.format()`
- **`str.join()`** for concatenating iterables — `", ".join(words)`; never `s += word` in a loop
- **Raw strings `r""`** for regex patterns and Windows paths
- **`.split()`** without arguments splits on any whitespace, handles multiple spaces/tabs/newlines
- **`.strip()` / `.lstrip()` / `.rstrip()`** for whitespace trimming

## 9. Context Managers

- **`with`** for all resource management (files, locks, connections) — guarantees cleanup even on exception
- **`@contextlib.contextmanager`** for simple generator-based CMs: code before `yield` is setup; always wrap `yield` in `try/finally` for guaranteed teardown
- **`contextlib.ExitStack`** for composing a dynamic number of context managers without nested `with` statements
- `__exit__` returning `True` suppresses the exception; returning `None`/`False` propagates it
