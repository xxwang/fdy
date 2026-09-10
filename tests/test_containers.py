import pytest

from fdy import containers


def test_deep_merge_nested():
    base = {"a": {"b": 1, "c": 2}, "d": 3}
    override = {"a": {"b": 9}, "e": 4}
    assert containers.deep_merge(base, override) == {
        "a": {"b": 9, "c": 2},
        "d": 3,
        "e": 4,
    }


def test_deep_merge_does_not_mutate_inputs():
    base = {"a": {"b": 1}}
    containers.deep_merge(base, {"a": {"b": 2}})
    assert base == {"a": {"b": 1}}


def test_deep_get_nested_mapping():
    assert containers.deep_get({"a": {"b": {"c": 1}}}, "a.b.c") == 1


def test_deep_get_sequence_index():
    assert containers.deep_get({"a": {"b": [10, 20, 30]}}, "a.b.2") == 30


def test_deep_get_returns_default_for_missing_path():
    assert containers.deep_get({"a": 1}, "a.b.c", default="x") == "x"


def test_deep_get_returns_default_for_out_of_range_index():
    assert containers.deep_get({"a": [1]}, "a.9", default=None) is None


def test_deep_get_empty_path():
    assert containers.deep_get({"a": 1}, "", default="x") == "x"


def test_deep_set_creates_intermediate_levels():
    data = {}
    containers.deep_set(data, "a.b.c", 1)
    assert data == {"a": {"b": {"c": 1}}}


def test_deep_set_replaces_non_mapping_intermediate():
    data = {"a": 5}
    containers.deep_set(data, "a.b", 1)
    assert data == {"a": {"b": 1}}


def test_flatten_nested_mapping():
    assert containers.flatten({"a": {"b": 1}, "c": 2}) == {"a.b": 1, "c": 2}


def test_flatten_keeps_empty_mapping_as_leaf():
    assert containers.flatten({"a": {}}) == {"a": {}}


def test_chunk_splits_with_remainder():
    assert list(containers.chunk([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_chunk_empty_input():
    assert list(containers.chunk([], 3)) == []


def test_chunk_rejects_invalid_size():
    with pytest.raises(ValueError):
        list(containers.chunk([1], 0))


def test_group_by_preserves_order():
    items = ["apple", "banana", "avocado", "blueberry"]
    result = containers.group_by(items, key=lambda word: word[0])
    assert result == {"a": ["apple", "avocado"], "b": ["banana", "blueberry"]}


def test_unique_preserves_first_seen_order():
    assert containers.unique([3, 1, 3, 2, 1]) == [3, 1, 2]


def test_unique_by_key():
    items = [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"}]
    assert containers.unique_by(items, key=lambda item: item["id"]) == [
        {"id": 1, "v": "a"},
        {"id": 2, "v": "c"},
    ]


def test_first_and_last():
    assert containers.first([1, 2, 3]) == 1
    assert containers.last([1, 2, 3]) == 3


def test_first_and_last_on_empty_sequence():
    assert containers.first([]) is None
    assert containers.last([], default="fallback") == "fallback"


def test_pick_and_omit():
    data = {"a": 1, "b": 2, "c": 3}
    assert containers.pick(data, ["a", "c", "missing"]) == {"a": 1, "c": 3}
    assert containers.omit(data, ["b"]) == {"a": 1, "c": 3}


def test_invert_swaps_keys_and_values():
    assert containers.invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}
