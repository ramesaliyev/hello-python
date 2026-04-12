# String operations: methods, formatting, encoding, and immutability.

import pytest

# ---------------------------------------------------------------------------
# 1. String methods
# ---------------------------------------------------------------------------


def test_split_on_whitespace_by_default() -> None:
    sentence = "  hello   world  "
    assert sentence.split() == ["hello", "world"]


def test_split_on_delimiter() -> None:
    csv_row = "a,b,c"
    assert csv_row.split(",") == ["a", "b", "c"]


def test_split_with_maxsplit() -> None:
    text = "one two three four"
    assert text.split(" ", maxsplit=2) == ["one", "two", "three four"]


def test_join_list_of_strings() -> None:
    words = ["hello", "world"]
    assert " ".join(words) == "hello world"
    assert ",".join(words) == "hello,world"
    assert "".join(words) == "helloworld"


def test_strip_removes_leading_and_trailing_whitespace() -> None:
    assert "  hello  ".strip() == "hello"
    assert "  hello  ".lstrip() == "hello  "
    assert "  hello  ".rstrip() == "  hello"


def test_strip_removes_specified_characters() -> None:
    # strips any combination of given chars, not a substring
    assert "xxhelloxx".strip("x") == "hello"
    assert "xyxhelloxyxy".strip("xy") == "hello"


def test_replace_substitutes_all_occurrences() -> None:
    assert "aabbcc".replace("b", "X") == "aaXXcc"


def test_replace_with_count_limits_substitutions() -> None:
    assert "aabbcc".replace("a", "X", 1) == "Xabbcc"


def test_find_returns_index_or_minus_one() -> None:
    assert "hello world".find("world") == 6
    assert "hello world".find("xyz") == -1


def test_index_raises_on_missing_substring() -> None:
    with pytest.raises(ValueError):
        "hello".index("xyz")


def test_startswith_and_endswith() -> None:
    filename = "report.pdf"
    assert filename.endswith(".pdf")
    assert not filename.endswith(".csv")
    assert filename.startswith("report")


def test_startswith_accepts_tuple_of_prefixes() -> None:
    # convenient for checking multiple options at once
    assert "hello".startswith(("hi", "he", "ho"))


def test_case_methods() -> None:
    assert "hello WORLD".upper() == "HELLO WORLD"
    assert "hello WORLD".lower() == "hello world"
    assert "hello world".title() == "Hello World"
    assert "Hello World".swapcase() == "hELLO wORLD"


def test_count_occurrences() -> None:
    assert "banana".count("a") == 3
    assert "banana".count("an") == 2


def test_strip_and_split_together() -> None:
    # common pattern: clean then split
    line = "  alice, bob, carol  "
    names = [name.strip() for name in line.strip().split(",")]
    assert names == ["alice", "bob", "carol"]


# ---------------------------------------------------------------------------
# 2. String formatting
# ---------------------------------------------------------------------------


def test_fstring_basic_interpolation() -> None:
    name = "world"
    assert f"hello {name}" == "hello world"


def test_fstring_expression_evaluation() -> None:
    assert f"{2 + 2}" == "4"
    assert f"{'hi'.upper()}" == "HI"


def test_fstring_format_spec_float() -> None:
    pi = 3.14159
    assert f"{pi:.2f}" == "3.14"


def test_fstring_format_spec_alignment() -> None:
    assert f"{'left':<10}" == "left      "  # 4 chars + 6 spaces = 10
    assert f"{'right':>10}" == "     right"  # 5 spaces + 5 chars = 10
    assert f"{'center':^10}" == "  center  "  # 2 + 6 + 2 = 10


def test_fstring_format_spec_integer() -> None:
    assert f"{255:08b}" == "11111111"  # binary, zero-padded to 8 chars
    assert f"{255:#x}" == "0xff"  # hex with prefix


def test_str_format_method() -> None:
    template = "Hello, {}! You are {} years old."
    assert template.format("Alice", 30) == "Hello, Alice! You are 30 years old."


def test_str_format_named_placeholders() -> None:
    assert "{name} is {age}".format(name="Bob", age=25) == "Bob is 25"


def test_percent_formatting() -> None:
    # legacy style — still valid, occasionally seen in older code
    assert "Hello, %s!" % "world" == "Hello, world!"  # noqa: UP031 — demonstrating legacy % formatting
    assert "Pi is %.2f" % 3.14159 == "Pi is 3.14"  # noqa: UP031 — demonstrating legacy % formatting


# ---------------------------------------------------------------------------
# 3. Raw strings and escape sequences
# ---------------------------------------------------------------------------


def test_escape_sequences() -> None:
    assert "line1\nline2".split("\n") == ["line1", "line2"]  # noqa: SIM905 — demonstrating split on escape sequence
    assert "col1\tcol2".split("\t") == ["col1", "col2"]  # noqa: SIM905 — demonstrating split on escape sequence
    assert 'quote: "hi"' == 'quote: "hi"'  # noqa: PLR0133 — demonstrating double-quote embedding in a string


def test_raw_string_disables_escape_sequences() -> None:
    # r"" treats backslashes as literal characters — common for regex and paths
    assert r"\n" == "\\n"  # noqa: PLR0133 — demonstrating raw string vs escape sequence equivalence
    assert len(r"\n") == 2


def test_multiline_string_with_triple_quotes() -> None:
    text = """line one
line two"""
    assert text.split("\n") == ["line one", "line two"]


# ---------------------------------------------------------------------------
# 4. String immutability
# ---------------------------------------------------------------------------


def test_strings_are_immutable() -> None:
    original = "hello"
    with pytest.raises(TypeError):
        original[0] = "H"  # type: ignore[index]


def test_string_operations_return_new_strings() -> None:
    original = "hello"
    upper = original.upper()
    assert upper == "HELLO"
    assert original == "hello"  # unchanged


# ---------------------------------------------------------------------------
# 5. Encoding and decoding
# ---------------------------------------------------------------------------


def test_encode_string_to_bytes() -> None:
    text = "hello"
    encoded = text.encode("utf-8")
    assert isinstance(encoded, bytes)
    assert encoded == b"hello"


def test_decode_bytes_to_string() -> None:
    raw = b"hello"
    assert raw.decode("utf-8") == "hello"


def test_encode_non_ascii_characters() -> None:
    text = "caf\u00e9"  # é is U+00E9
    encoded = text.encode("utf-8")
    assert len(encoded) > len(text)  # é takes 2 bytes in UTF-8
    assert encoded.decode("utf-8") == text


def test_encode_error_handling() -> None:
    # ascii codec cannot encode é — raises by default
    with pytest.raises(UnicodeEncodeError):
        "café".encode("ascii")


def test_encode_with_replace_error_handler() -> None:
    result = "café".encode("ascii", errors="replace")
    assert result == b"caf?"


def test_encode_with_ignore_error_handler() -> None:
    result = "café".encode("ascii", errors="ignore")
    assert result == b"caf"
