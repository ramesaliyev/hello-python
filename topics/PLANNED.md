# Planned Topics

## Roadmap

Agreed learning sequence:

1. **itertools** — finishes the functions/iterables chapter before moving on
2. **OOP** — classes, inheritance, protocols, dataclasses, enums, metaclasses
3. **Concurrency** — threads, multiprocessing, asyncio
4. **Type hints (capstone)** — dedicate a topic once everything else is known; then do a retroactive pass to annotate existing code where possible. The `topics/type_hints/` folder runs mypy in strict mode — that's intentional and only applies there.

---

## itertools — `functions/itertools/`

Fits under `functions/` alongside `basics/`, `generators/`, `decorators/` — it extends the iterables/generators world already covered there.

- [infinite iterators](tests/test_infinite.py) — `count`, `cycle`, `repeat`: iterators that never stop; pairing with `islice` to cap them
- [slicing and chaining](tests/test_slicing_chaining.py) — `islice`, `chain`, `chain.from_iterable`, `zip_longest`, `pairwise`: reshaping and combining iterables
- [filtering and mapping](tests/test_filtering_mapping.py) — `compress`, `dropwhile`, `takewhile`, `filterfalse`, `starmap`, `accumulate`: predicate-based filtering and running aggregations
- [combinatorics](tests/test_combinatorics.py) — `product`, `permutations`, `combinations`, `combinations_with_replacement`, `groupby`: Cartesian products, ordered/unordered selections, grouping sorted data

**Resources:**
- [Python Docs — itertools](https://docs.python.org/3/library/itertools.html)
- [Python Docs — itertools recipes](https://docs.python.org/3/library/itertools.html#itertools-recipes)
- [Real Python — itertools](https://realpython.com/python-itertools/)

---

## OOP

### classes — `oop/classes/`

- [dunder lifecycle](tests/test_dunder_lifecycle.py) — `__new__`, `__init__`, `__del__`: object construction, initialization, and finalization lifecycle
- [dunder representation](tests/test_dunder_representation.py) — `__repr__`, `__str__`, `__bytes__`, `__format__`: how objects render themselves as strings and bytes
- [dunder comparison](tests/test_dunder_comparison.py) — `__eq__`, `__ne__`, `__lt__`/`__le__`/`__gt__`/`__ge__`, `__hash__`, `__bool__`: rich comparison and truthiness protocol
- [dunder container](tests/test_dunder_container.py) — `__len__`, `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, `__next__`, `__reversed__`: container and iterator protocol
- [dunder arithmetic](tests/test_dunder_arithmetic.py) — `__add__`/`__radd__`/`__iadd__` families and the full numeric protocol
- [dunder attribute access](tests/test_dunder_attribute_access.py) — `__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__`: attribute lookup and interception
- [dunder callable and context manager](tests/test_dunder_callable_context.py) — `__call__` for callable objects; `__enter__`/`__exit__` for context manager protocol
- [decorators](tests/test_decorators.py) — `@classmethod`, `@staticmethod`, `@property`/`@x.setter`/`@x.deleter`, `@final`, `@override`
- [class vs instance variables](tests/test_class_vs_instance_vars.py) — class vs instance variables, the shadowing gotcha, mutation of shared state
- [slots](tests/test_slots.py) — `__slots__`: memory savings, attribute restriction, inheritance gotchas
- [descriptors](tests/test_descriptors.py) — descriptor protocol (`__get__`, `__set__`, `__delete__`), data vs non-data descriptors, `__set_name__`, functions as non-data descriptors (how method binding works, `types.MethodType`), `property`/`classmethod`/`staticmethod` internals. **Note:** this is the primary home for all descriptor content — do not add descriptor/`__get__` material to `topics/functions/`. The decorator topic (`functions/decorators/tests/test_class_based.py` sections 3–4) already has inline context; reference it here as "you've seen this in action." But still explain the whole thing in detail.

**Resources:**
- [Python Docs — Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Python Docs — Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html)
- [Real Python — Python Classes](https://realpython.com/python3-object-oriented-programming/)
- [Real Python — Slots](https://realpython.com/python-slots/)
- [Python Morsels — Every dunder method](https://www.pythonmorsels.com/every-dunder-method/)

### inheritance — `oop/inheritance/`

- [single inheritance](tests/test_single_inheritance.py) — basic parent-child relationships, method overriding, `super()` in simple chains
- [multiple inheritance](tests/test_multiple_inheritance.py) — multiple parent classes, diamond problem, method resolution ambiguity
- [method resolution order](tests/test_mro.py) — C3 linearization algorithm, `__mro__`, `mro()`, MRO gotchas with complex hierarchies
- [super()](tests/test_super.py) — cooperative inheritance, `super()` in multiple inheritance, call order guarantees
- [mixins](tests/test_mixins.py) — mixin pattern, composing behavior without deep inheritance, composition vs inheritance trade-offs
- [abstract base classes](tests/test_abstract_base_classes.py) — `ABC`, `ABCMeta`, `@abstractmethod`, preventing instantiation of abstract classes

**Resources:**
- [Python Docs — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Python Docs — Multiple Inheritance](https://docs.python.org/3/tutorial/classes.html#multiple-inheritance)
- [Python Docs — abc module](https://docs.python.org/3/library/abc.html)
- [Python Docs — MRO](https://docs.python.org/3/howto/mro.html)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)

### protocols — `oop/protocols/`

- [protocols](tests/test_protocols.py) — `typing.Protocol`, `@runtime_checkable`, structural vs nominal subtyping, `isinstance` gotchas with protocols

**Resources:**
- [Python Docs — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Real Python — Python Protocols](https://realpython.com/python-protocol/)
- [mypy — Protocols](https://mypy.readthedocs.io/en/stable/protocols.html)

### dataclasses — `oop/dataclasses/`

- [dataclasses](tests/test_dataclasses.py) — `@dataclass` parameters (`eq`, `order`, `frozen`, `slots`), `field()` defaults and metadata, `__post_init__`, comparison with `NamedTuple`

**Resources:**
- [Python Docs — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/)
- [Real Python — Dataclasses](https://realpython.com/python-data-classes/)

### enums — `oop/enums/`

- [enums](tests/test_enums.py) — `Enum`, `IntEnum`, `Flag`, `IntFlag`, `StrEnum`, `auto()`, member access patterns, iteration, comparison gotchas

**Resources:**
- [Python Docs — enum](https://docs.python.org/3/library/enum.html)
- [PEP 435 — Adding an Enum type to Python](https://peps.python.org/pep-0435/)
- [Real Python — Enumerations in Python](https://realpython.com/python-enum/)

### metaclasses — `oop/metaclasses/`

- [metaclasses](tests/test_metaclasses.py) — `type` as a metaclass, creating custom metaclasses, `__init_subclass__`, `__class_getitem__`, when metaclasses are appropriate vs alternatives

**Resources:**
- [Python Docs — Metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses)
- [Python Docs — __init_subclass__](https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__)
- [Real Python — Metaclasses](https://realpython.com/python-metaclasses/)
- [PEP 487 — Simpler class creation customisation](https://peps.python.org/pep-0487/)
