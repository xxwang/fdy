import hashlib

import pytest

from fdy import files


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (0, "0 B"),
        (512, "512 B"),
        (1023, "1023 B"),
        (1024, "1 KB"),
        (1536, "1.5 KB"),
        (2048, "2 KB"),
        (5 * 1024**3, "5 GB"),
    ],
)
def test_human_size(size, expected):
    assert files.human_size(size) == expected


def test_human_size_respects_precision():
    assert files.human_size(1536, precision=3) == "1.5 KB"
    assert files.human_size(1234567, precision=3) == "1.177 MB"


def test_human_size_supports_exabyte():
    assert files.human_size(1024**6) == "1 EB"


def test_human_size_rejects_negative():
    with pytest.raises(ValueError):
        files.human_size(-1)


def test_ensure_dir_creates_nested_directory(tmp_path):
    target = files.ensure_dir(tmp_path / "a" / "b" / "c")
    assert target.is_dir()


def test_ensure_dir_is_idempotent(tmp_path):
    target = tmp_path / "a"
    files.ensure_dir(target)
    assert files.ensure_dir(target).is_dir()


def test_write_and_read_text_roundtrip(tmp_path):
    target = tmp_path / "nested" / "note.txt"
    files.write_text(target, "你好")
    assert target.exists()
    assert files.read_text(target) == "你好"


def test_read_text_returns_default_when_missing(tmp_path):
    assert files.read_text(tmp_path / "missing.txt", default="fallback") == "fallback"
    assert files.read_text(tmp_path / "missing.txt") is None


def test_write_and_read_json_roundtrip(tmp_path):
    target = tmp_path / "data" / "config.json"
    files.write_json(target, {"name": "张三", "items": [1, 2]})
    assert files.read_json(target) == {"name": "张三", "items": [1, 2]}


def test_write_json_keeps_chinese_readable(tmp_path):
    target = tmp_path / "data.json"
    files.write_json(target, {"name": "张三"})
    assert "张三" in target.read_text(encoding="utf-8")


def test_read_json_returns_default_for_invalid_content(tmp_path):
    target = tmp_path / "broken.json"
    target.write_text("{ not json", encoding="utf-8")
    assert files.read_json(target, default={}) == {}


def test_iter_files_recursive(tmp_path):
    files.write_text(tmp_path / "top.txt", "a")
    files.write_text(tmp_path / "sub" / "deep.txt", "b")
    files.write_text(tmp_path / "sub" / "deep.md", "c")
    assert {item.name for item in files.iter_files(tmp_path)} == {
        "top.txt",
        "deep.txt",
        "deep.md",
    }


def test_iter_files_non_recursive(tmp_path):
    files.write_text(tmp_path / "top.txt", "a")
    files.write_text(tmp_path / "sub" / "deep.txt", "b")
    assert {item.name for item in files.iter_files(tmp_path, recursive=False)} == {
        "top.txt"
    }


def test_iter_files_filters_by_pattern(tmp_path):
    files.write_text(tmp_path / "a.py", "")
    files.write_text(tmp_path / "b.txt", "")
    assert {item.name for item in files.iter_files(tmp_path, pattern="*.py")} == {
        "a.py"
    }


def test_iter_files_yields_nothing_for_missing_root(tmp_path):
    assert list(files.iter_files(tmp_path / "missing")) == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("report.txt", "report.txt"),
        ("a/b:c*d?.txt", "a_b_c_d_.txt"),
        ("  report.txt  ", "report.txt"),
        ("...", "untitled"),
        ("", "untitled"),
        (".env", ".env"),
        (".gitignore", ".gitignore"),
        ("file.", "file"),
    ],
)
def test_safe_filename(source, expected):
    assert files.safe_filename(source) == expected


def test_unique_path_returns_original_when_free(tmp_path):
    target = tmp_path / "file.txt"
    assert files.unique_path(target) == target


def test_unique_path_appends_index(tmp_path):
    target = tmp_path / "file.txt"
    files.write_text(target, "x")
    assert files.unique_path(target) == tmp_path / "file (1).txt"


def test_unique_path_increments_until_free(tmp_path):
    files.write_text(tmp_path / "file.txt", "x")
    files.write_text(tmp_path / "file (1).txt", "x")
    assert files.unique_path(tmp_path / "file.txt") == tmp_path / "file (2).txt"


def test_file_hash_matches_hashlib(tmp_path):
    target = files.write_text(tmp_path / "blob.bin", "hello")
    expected = hashlib.sha256(b"hello").hexdigest()
    assert files.file_hash(target) == expected


def test_file_hash_supports_other_algorithms(tmp_path):
    target = files.write_text(tmp_path / "blob.bin", "hello")
    assert files.file_hash(target, algorithm="md5") == hashlib.md5(b"hello").hexdigest()


def test_file_hash_returns_default_for_missing_file():
    assert files.file_hash("/nonexistent/file", default="") == ""
    assert files.file_hash("/nonexistent/file") is None
