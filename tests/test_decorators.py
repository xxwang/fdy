import time

import pytest

from fdy import decorators


def test_timer_returns_wrapped_result():
    @decorators.timer(log=False)
    def work():
        return "done"

    assert work() == "done"


def test_timer_records_elapsed_time():
    @decorators.timer(log=False)
    def slow():
        time.sleep(0.01)

    slow()
    assert slow.last_elapsed >= 0.005


def test_timer_works_without_parentheses():
    @decorators.timer
    def work():
        return 1

    assert work() == 1
    assert work.last_elapsed >= 0


def test_timer_logs_message(caplog):
    @decorators.timer
    def work():
        return 1

    with caplog.at_level("INFO", logger="fdy"):
        work()
    assert "耗时" in caplog.text


def test_retry_returns_result_without_retrying():
    calls = {"n": 0}

    @decorators.retry(times=3, delay=0)
    def ok():
        calls["n"] += 1
        return "ok"

    assert ok() == "ok"
    assert calls["n"] == 1


def test_retry_keeps_trying_until_success():
    calls = {"n": 0}

    @decorators.retry(times=3, delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3


def test_retry_reraises_after_exhausting_attempts():
    calls = {"n": 0}

    @decorators.retry(times=2, delay=0, exceptions=(ValueError,))
    def always_fails():
        calls["n"] += 1
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        always_fails()
    assert calls["n"] == 2


def test_retry_ignores_unlisted_exceptions():
    @decorators.retry(times=3, delay=0, exceptions=(ValueError,))
    def raises_type_error():
        raise TypeError("nope")

    with pytest.raises(TypeError):
        raises_type_error()


def test_retry_rejects_invalid_times():
    with pytest.raises(ValueError):
        decorators.retry(times=0)


def test_retry_preserves_function_metadata():
    @decorators.retry(times=2, delay=0)
    def documented():
        """原始文档字符串。"""

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "原始文档字符串。"


def test_memoize_caches_repeated_calls():
    calls = {"n": 0}

    @decorators.memoize
    def square(value):
        calls["n"] += 1
        return value * value

    assert square(3) == 9
    assert square(3) == 9
    assert calls["n"] == 1


def test_memoize_distinguishes_arguments():
    calls = {"n": 0}

    @decorators.memoize
    def identity(value, scale=1):
        calls["n"] += 1
        return value * scale

    identity(2)
    identity(3)
    identity(2, scale=2)
    assert calls["n"] == 3


def test_memoize_cache_clear():
    calls = {"n": 0}

    @decorators.memoize
    def square(value):
        calls["n"] += 1
        return value * value

    square(3)
    square.cache_clear()
    square(3)
    assert calls["n"] == 2


def test_memoize_falls_back_for_unhashable_arguments():
    @decorators.memoize
    def total(items):
        return sum(items)

    assert total([1, 2, 3]) == 6
    assert total([1, 2, 3]) == 6


def test_silent_returns_default_on_expected_exception():
    @decorators.silent(default=-1, exceptions=(ValueError,))
    def explodes():
        raise ValueError("boom")

    assert explodes() == -1


def test_silent_lets_other_exceptions_through():
    @decorators.silent(default=-1, exceptions=(ValueError,))
    def explodes():
        raise TypeError("boom")

    with pytest.raises(TypeError):
        explodes()


def test_silent_keeps_arguments_working():
    @decorators.silent(default=0)
    def add(left, right):
        if left < 0:
            raise ValueError("负数不支持")
        return left + right

    assert add(1, 2) == 3
    assert add(-1, 2) == 0


def test_singleton_returns_same_instance():
    @decorators.singleton
    class Config:
        pass

    assert Config() is Config()


def test_singleton_keeps_distinct_classes_separate():
    @decorators.singleton
    class First:
        pass

    @decorators.singleton
    class Second:
        pass

    assert First() is not Second()
