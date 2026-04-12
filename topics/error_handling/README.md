# Error Handling

## Examples

- [basics](tests/test_basics.py) — try/except/else/finally, exception hierarchy, variable scope, PEP 765
- [raising](tests/test_raising.py) — raise, re-raise, explicit/implicit chaining, exception attributes
- [custom exceptions](tests/test_custom_exceptions.py) — custom exception classes, hierarchy, add_note(), args and str
- [exception groups](tests/test_exception_groups.py) — ExceptionGroup, except*, BaseExceptionGroup, subgroup(), split()
- [suppression](tests/test_suppression.py) — contextlib.suppress, __exit__ returning True, practical patterns

## Resources

- [Python Docs — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python Docs — Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [PEP 654 — Exception Groups and except*](https://peps.python.org/pep-0654/)
- [PEP 678 — Enriching Exceptions with Notes (add_note)](https://peps.python.org/pep-0678/)
- [PEP 765 — Disallow return/break/continue inside finally](https://peps.python.org/pep-0765/)
- [Real Python — Exception Handling](https://realpython.com/python-exceptions/)
- [Real Python — Exception Groups](https://realpython.com/python-exception-groups/)
