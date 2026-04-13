# Decorators

## Examples

- [basics](tests/test_basics.py) — @-syntax, wrapping args/kwargs/return values, side-effects, identity loss
- [stacking](tests/test_stacking.py) — application order (bottom-up), execution order (outermost first), order-dependent behaviour
- [functools](tests/test_functools.py) — wraps, update_wrapper, lru_cache, cache, cached_property, total_ordering
- [parameterized](tests/test_parameterized.py) — factory pattern, optional-argument decorators, forgetting-to-call-the-factory gotcha
- [class-based](tests/test_class_based.py) — __call__, stateful decorators, __get__ for method binding, class decorators

## Resources

- [Python Docs — Glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator)
- [Python Docs — functools](https://docs.python.org/3/library/functools.html)
- [PEP 318 — Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
- [PEP 3129 — Class Decorators](https://peps.python.org/pep-3129/)
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Real Python — Caching in Python Using the LRU Cache Strategy](https://realpython.com/lru-cache-python/)
