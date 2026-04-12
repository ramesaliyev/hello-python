# Context Managers

## Examples

- [protocol](tests/test_protocol.py) — `__enter__`/`__exit__` protocol, error edge cases (`__enter__` raising skips `__exit__`, `__exit__` raising masks original exception), practical resource patterns
- [decorator](tests/test_decorator.py) — `@contextmanager` decorator, cleanup via `finally`, exception suppression in generators, using as a function decorator
- [multiple context managers](tests/test_multiple_cms.py) — stacking CMs in one `with` statement, LIFO exit order, all CMs exit even on exception
- [contextlib](tests/test_contextlib.py) — `suppress`, `closing`, `nullcontext`, `ExitStack`
- [async context managers](tests/test_async_cms.py) — `__aenter__`/`__aexit__` protocol, `async with`, `@asynccontextmanager`

## Related sections

- **Exception suppression patterns** and `__exit__` mechanics in depth: [error handling — suppression](../error_handling/tests/test_suppression.py)
- **Advanced async CM patterns** (trio, anyio, `TaskGroup`, structured concurrency): `topics/asyncio/` *(upcoming, @TODO)*

## Resources

- [Python Docs — with statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)
- [Python Docs — contextlib](https://docs.python.org/3/library/contextlib.html)
- [Python Docs — Async Context Managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
- [PEP 343 — The with Statement](https://peps.python.org/pep-0343/)
- [Real Python — Context Managers and the `with` Statement](https://realpython.com/python-with-statement/)
