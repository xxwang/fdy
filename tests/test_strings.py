import pytest

from fdy import strings


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("HTTPServerConfig", "http_server_config"),
        ("userID", "user_id"),
        ("hello world", "hello_world"),
        ("kebab-case-name", "kebab_case_name"),
        ("already_snake", "already_snake"),
        ("", ""),
    ],
)
def test_snake_case(source, expected):
    assert strings.snake_case(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("user_profile", "user-profile"),
        ("HTTPServerConfig", "http-server-config"),
    ],
)
def test_kebab_case(source, expected):
    assert strings.kebab_case(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("user_profile", "userProfile"),
        ("HTTPServer", "httpServer"),
        ("", ""),
    ],
)
def test_camel_case(source, expected):
    assert strings.camel_case(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("user_profile", "UserProfile"),
        ("userID", "UserId"),
        ("", ""),
    ],
)
def test_pascal_case(source, expected):
    assert strings.pascal_case(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Hello World!", "hello-world"),
        ("  Hello---World  ", "hello-world"),
        ("已经-raised", "raised"),
    ],
)
def test_slugify(source, expected):
    assert strings.slugify(source) == expected


def test_truncate_keeps_short_text():
    assert strings.truncate("abc", 10) == "abc"


def test_truncate_appends_suffix():
    assert strings.truncate("hello world", 8) == "hello..."


def test_truncate_without_suffix():
    assert strings.truncate("abcdef", 3, suffix="") == "abc"


def test_truncate_when_suffix_longer_than_limit():
    assert strings.truncate("hello", 2) == ".."


def test_truncate_rejects_negative_length():
    with pytest.raises(ValueError):
        strings.truncate("abc", -1)


def test_mask_phone_number():
    assert strings.mask("13812345678", 3, 4) == "138****5678"


def test_mask_keeps_value_when_nothing_to_hide():
    assert strings.mask("ab", 1, 1) == "ab"


def test_mask_without_visible_edges():
    assert strings.mask("secret") == "******"


def test_mask_rejects_negative_keep():
    with pytest.raises(ValueError):
        strings.mask("abc", -1, 0)


def test_random_string_length_and_alphabet():
    token = strings.random_string(12, "ab")
    assert len(token) == 12
    assert set(token) <= {"a", "b"}


def test_random_string_default_alphabet_is_alphanumeric():
    token = strings.random_string(32)
    assert token.isalnum()


def test_random_string_rejects_empty_alphabet():
    with pytest.raises(ValueError):
        strings.random_string(4, "")


def test_normalize_space():
    assert strings.normalize_space("  a \n\t b  ") == "a b"
