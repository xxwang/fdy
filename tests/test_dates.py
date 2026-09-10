from datetime import UTC, date, datetime, timedelta

import pytest

from fdy import dates


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("2024-01-02 03:04:05", datetime(2024, 1, 2, 3, 4, 5)),
        ("2024-01-02T03:04:05", datetime(2024, 1, 2, 3, 4, 5)),
        ("2024-01-02", datetime(2024, 1, 2)),
        ("2024/01/02", datetime(2024, 1, 2)),
        ("20240102", datetime(2024, 1, 2)),
    ],
)
def test_parse_datetime_common_formats(source, expected):
    assert dates.parse_datetime(source) == expected


def test_parse_datetime_returns_default_on_failure():
    assert dates.parse_datetime("不是日期", default=None) is None


def test_parse_datetime_returns_default_for_non_string():
    assert dates.parse_datetime(12345, default=None) is None


def test_parse_datetime_passes_through_datetime():
    moment = datetime(2024, 1, 2, 3, 4, 5)
    assert dates.parse_datetime(moment) is moment


def test_parse_datetime_converts_date_to_utc_datetime():
    assert dates.parse_datetime(date(2024, 1, 2)) == datetime(2024, 1, 2, tzinfo=UTC)


def test_parse_datetime_handles_iso_with_offset():
    parsed = dates.parse_datetime("2024-01-02T03:04:05+08:00")
    assert parsed.utcoffset() == timedelta(hours=8)


def test_format_datetime():
    assert dates.format_datetime("2024-01-02 03:04:05", "%Y/%m/%d") == "2024/01/02"


def test_format_datetime_uses_default_on_failure():
    assert dates.format_datetime("乱码", default="N/A") == "N/A"


def test_to_timestamp_of_epoch():
    assert dates.to_timestamp("1970-01-01T00:00:00+00:00") == 0.0


def test_to_timestamp_treats_naive_as_utc():
    assert dates.to_timestamp("1970-01-01 00:00:00") == 0.0


def test_to_timestamp_uses_default_on_failure():
    assert dates.to_timestamp("乱码", default=-1.0) == -1.0


def test_from_timestamp_roundtrip():
    moment = dates.from_timestamp(0)
    assert moment == datetime(1970, 1, 1, tzinfo=UTC)


def test_now_is_timezone_aware():
    assert dates.now().tzinfo is UTC


@pytest.mark.parametrize(
    ("delta", "expected"),
    [
        (timedelta(seconds=5), "刚刚"),
        (timedelta(seconds=30), "30 秒前"),
        (timedelta(seconds=90), "1 分钟前"),
        (timedelta(hours=3), "3 小时前"),
        (timedelta(days=1), "1 天前"),
        (timedelta(days=-1), "1 天后"),
        (timedelta(seconds=-7200), "2 小时后"),
    ],
)
def test_humanize_delta_with_timedelta(delta, expected):
    assert dates.humanize_delta(delta) == expected


def test_humanize_delta_accepts_seconds():
    assert dates.humanize_delta(-7200) == "2 小时后"
    assert dates.humanize_delta(0) == "刚刚"


def test_humanize_delta_returns_default_for_unparsable_input():
    assert dates.humanize_delta("乱码", default="-") == "-"


def test_days_between():
    assert dates.days_between("2024-01-01", "2024-01-11") == 10
    assert dates.days_between("2024-01-11", "2024-01-01") == -10


def test_days_between_rejects_unparsable_input():
    with pytest.raises(ValueError):
        dates.days_between("乱码", "2024-01-01")


def test_date_range_is_inclusive():
    assert list(dates.date_range("2024-01-01", "2024-01-05")) == [
        date(2024, 1, 1),
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
        date(2024, 1, 5),
    ]


def test_date_range_with_step():
    assert list(dates.date_range("2024-01-01", "2024-01-07", step_days=3)) == [
        date(2024, 1, 1),
        date(2024, 1, 4),
        date(2024, 1, 7),
    ]


def test_date_range_rejects_reversed_bounds():
    with pytest.raises(ValueError):
        list(dates.date_range("2024-01-05", "2024-01-01"))


def test_date_range_rejects_non_positive_step():
    with pytest.raises(ValueError):
        list(dates.date_range("2024-01-01", "2024-01-05", step_days=0))


def test_start_and_end_of_day():
    assert dates.start_of_day("2024-01-02 13:45:00") == datetime(2024, 1, 2)
    assert dates.end_of_day("2024-01-02 13:45:00") == datetime(
        2024, 1, 2, 23, 59, 59, 999999
    )


def test_start_of_day_preserves_timezone():
    parsed = dates.start_of_day("2024-01-02T13:45:00+08:00")
    assert parsed.utcoffset() == timedelta(hours=8)
    assert parsed.hour == 0


def test_start_of_month():
    assert dates.start_of_month("2024-01-15 08:00:00") == datetime(2024, 1, 1)


def test_day_boundaries_reject_unparsable_input():
    with pytest.raises(ValueError):
        dates.start_of_day("乱码")
