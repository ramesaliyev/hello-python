# Async generators: async def + yield, async for, anext(), aclose(), athrow().

import asyncio
from collections.abc import AsyncGenerator
import types

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def async_range(stop: int) -> AsyncGenerator[int]:
    for i in range(stop):
        yield i


# ---------------------------------------------------------------------------
# 1. Basics
# ---------------------------------------------------------------------------


async def test_async_generator_function_syntax() -> None:
    agen = async_range(3)
    # Calling an async generator function returns an async generator object
    assert isinstance(agen, types.AsyncGeneratorType)
    await agen.aclose()


async def test_async_for_drives_async_generator() -> None:
    result: list[int] = []
    async for value in async_range(4):
        result.append(value)  # noqa: PERF401 — teaching async for explicitly
    assert result == [0, 1, 2, 3]


async def test_async_generator_preserves_state_between_yields() -> None:
    async def counter() -> AsyncGenerator[int]:
        count = 0
        yield count
        count += 1
        yield count
        count += 1
        yield count

    gen = counter()
    assert await anext(gen) == 0
    assert await anext(gen) == 1
    assert await anext(gen) == 2


async def test_async_generator_can_contain_await_expressions() -> None:
    async def slow_range(stop: int) -> AsyncGenerator[int]:
        for i in range(stop):
            await asyncio.sleep(0)  # simulate async I/O — key differentiator from sync
            yield i

    result = [value async for value in slow_range(3)]
    assert result == [0, 1, 2]


# ---------------------------------------------------------------------------
# 2. Protocol
# ---------------------------------------------------------------------------


async def test_anext_advances_async_generator_by_one() -> None:
    gen = async_range(3)
    assert await anext(gen) == 0
    assert await anext(gen) == 1
    assert await anext(gen) == 2


async def test_anext_with_default_avoids_stopasynciteration() -> None:
    gen = async_range(1)
    assert await anext(gen) == 0
    # When exhausted, returns the default instead of raising StopAsyncIteration
    result = await anext(gen, None)
    assert result is None


async def test_async_generator_raises_stopasynciteration_when_exhausted() -> None:
    gen = async_range(1)
    await anext(gen)
    with pytest.raises(StopAsyncIteration):
        await anext(gen)


async def test_async_generator_expression_syntax() -> None:
    # Async comprehensions use 'async for' to consume an async generator
    result = [x * 2 async for x in async_range(4)]
    assert result == [0, 2, 4, 6]


# ---------------------------------------------------------------------------
# 3. Lifecycle
# ---------------------------------------------------------------------------


async def test_aclose_terminates_async_generator() -> None:
    gen = async_range(100)
    await anext(gen)  # start it
    await gen.aclose()  # terminate early

    # Subsequent reads raise StopAsyncIteration
    with pytest.raises(StopAsyncIteration):
        await anext(gen)


async def test_async_generator_finally_block_runs_on_aclose() -> None:
    cleanup_log: list[str] = []

    async def gen() -> AsyncGenerator[int]:
        try:
            yield 1
            yield 2
        finally:
            cleanup_log.append("cleanup")

    agen = gen()
    await anext(agen)
    await agen.aclose()

    assert cleanup_log == ["cleanup"]


async def test_athrow_injects_exception_into_async_generator() -> None:
    caught: list[str] = []

    async def gen() -> AsyncGenerator[int]:
        try:
            yield 1
        except ValueError as exc:
            caught.append(str(exc))
            yield 2

    agen = gen()
    await anext(agen)  # advance to first yield
    next_value = await agen.athrow(ValueError("injected"))

    assert caught == ["injected"]
    assert next_value == 2


# ---------------------------------------------------------------------------
# 4. Pitfalls
# ---------------------------------------------------------------------------


async def test_async_generator_is_not_a_coroutine() -> None:
    # Async generator objects cannot be awaited — iterate with async for or anext()
    agen = async_range(3)
    with pytest.raises(TypeError):
        await agen  # type: ignore[misc]  # intentional: async generator objects cannot be awaited
    await agen.aclose()


async def test_async_generator_cannot_use_yield_from() -> None:
    # yield from is not allowed inside async generators (PEP 525)
    # Use 'async for' to iterate another async generator inside an async generator
    with pytest.raises(SyntaxError):
        compile(
            "async def gen():\n    yield from [1, 2, 3]",
            "<string>",
            "exec",
        )


async def test_async_generator_cannot_use_return_with_value() -> None:
    # return with a value is a SyntaxError in async generators (PEP 525)
    # Use a bare return to stop early, or just let the function end naturally
    with pytest.raises(SyntaxError):
        compile(
            'async def gen():\n    yield 1\n    return "done"',
            "<string>",
            "exec",
        )
