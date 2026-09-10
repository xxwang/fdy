import string
import uuid

import pytest

from fdy import ids


def test_uuid_str_is_valid_uuid4():
    value = ids.uuid_str()
    assert ids.is_valid_uuid(value)
    assert ids.is_valid_uuid(value, version=4)


def test_is_valid_uuid_rejects_garbage():
    assert ids.is_valid_uuid("not-a-uuid") is False
    assert ids.is_valid_uuid(None) is False
    assert ids.is_valid_uuid("") is False


def test_is_valid_uuid_checks_version():
    uuid1 = str(uuid.uuid1())
    assert ids.is_valid_uuid(uuid1, version=1) is True
    assert ids.is_valid_uuid(uuid1, version=4) is False


def test_uuid_str_values_are_unique():
    assert len({ids.uuid_str() for _ in range(100)}) == 100


def test_short_id_length_and_alphabet():
    value = ids.short_id(16)
    assert len(value) == 16
    assert set(value) <= set(ids._SAFE_ALPHABET)


def test_short_id_excludes_ambiguous_characters():
    alphabet = set(ids._SAFE_ALPHABET)
    assert not alphabet & set("0O1lI")


def test_short_id_accepts_custom_alphabet():
    value = ids.short_id(8, "xy")
    assert len(value) == 8
    assert set(value) <= {"x", "y"}


def test_short_id_rejects_non_positive_length():
    with pytest.raises(ValueError):
        ids.short_id(0)
    with pytest.raises(ValueError):
        ids.short_id(-3)


def test_token_hex_has_double_length():
    token = ids.token_hex(8)
    assert len(token) == 16
    assert set(token) <= set(string.hexdigits)


def test_token_hex_values_are_unique():
    assert len({ids.token_hex(16) for _ in range(50)}) == 50


def test_token_urlsafe_is_url_safe():
    token = ids.token_urlsafe(16)
    assert set(token) <= set(string.ascii_letters + string.digits + "-_")
