# Planned Topics

## Functions

### decorators — `functions/decorators/`

- [decorators](tests/test_decorators.py) — function decorators, stacking, parameterized decorators, `functools.wraps`

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
- [descriptors](tests/test_descriptors.py) — descriptor protocol (`__get__`, `__set__`, `__delete__`), data vs non-data descriptors

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
