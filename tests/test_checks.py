import pytest

from fdy import checks


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("YES", True),
        ("on", True),
        ("false", False),
        ("Off", False),
        ("none", False),
        ("", False),
        ("随便写的文本", True),
    ],
)
def test_to_bool(value, expected):
    assert checks.to_bool(value) is expected


def test_to_int_parses_numeric_strings():
    assert checks.to_int("42") == 42
    assert checks.to_int("1e2") == 100


def test_to_int_truncates_floats():
    assert checks.to_int("12.7") == 12


def test_to_int_uses_default_on_failure():
    assert checks.to_int("abc", default=-1) == -1
    assert checks.to_int(None, default=-1) == -1


def test_to_float():
    assert checks.to_float("3.14") == pytest.approx(3.14)
    assert checks.to_float("nope", default=0.5) == 0.5


def test_safe_cast_applies_converter():
    assert checks.safe_cast("5", int) == 5


def test_safe_cast_returns_default_on_error():
    assert checks.safe_cast("abc", int, default=-1) == -1


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, True),
        ("", True),
        ([], True),
        ({}, True),
        (set(), True),
        (0, False),
        (False, False),
        ("x", False),
        ([1], False),
        ({"a": 1}, False),
    ],
)
def test_is_empty(value, expected):
    assert checks.is_empty(value) is expected


def test_is_empty_leaves_generators_untouched():
    generator = (item for item in [1, 2])
    assert checks.is_empty(generator) is False
    assert list(generator) == [1, 2]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, True),
        ("   ", True),
        ("\n\t", True),
        ("", True),
        ("x", False),
        (0, False),
    ],
)
def test_is_blank(value, expected):
    assert checks.is_blank(value) is expected


def test_is_iterable_treats_text_as_scalar():
    assert checks.is_iterable([1, 2]) is True
    assert checks.is_iterable((1, 2)) is True
    assert checks.is_iterable("abc") is False
    assert checks.is_iterable(b"abc") is False
    assert checks.is_iterable(5) is False


def test_ensure_list_variants():
    assert checks.ensure_list(None) == []
    assert checks.ensure_list("abc") == ["abc"]
    assert checks.ensure_list((1, 2)) == [1, 2]
    assert checks.ensure_list(5) == [5]


def test_ensure_list_returns_same_list_object():
    original = [1, 2]
    assert checks.ensure_list(original) is original
