from typing import Any

import pytest
from pydantic import ValidationError

import fdy
from fdy import FAIL_CODE, OK_CODE, Resp


def _bad(value: Any) -> Any:
    """负例专用：擦除静态类型，让非法调用只在运行期暴露。"""
    return value


def test_public_constant_values():
    """锁死公开常量的协议值，改动必须是有意的。"""
    assert OK_CODE == 0
    assert FAIL_CODE == 1


def test_message_default_is_internal_only():
    """默认文案只作内部默认值，不对外导出。"""
    assert "OK_MESSAGE" not in fdy.__all__
    assert not hasattr(fdy, "OK_MESSAGE")
    assert not hasattr(fdy.models, "OK_MESSAGE")
    assert not hasattr(fdy.models.resp, "OK_MESSAGE")
    assert fdy.models.resp._OK_MESSAGE == "success"


def test_default_values():
    r = Resp()
    assert r.code == 0
    assert r.message == "success"
    assert r.data is None


def test_resp_ok_defaults():
    r = Resp.ok()
    assert r.code == 0
    assert r.message == "success"
    assert r.data is None


def test_resp_ok_overrides():
    r = Resp.ok(code=200, message="done", data=[1, 2])
    assert r.code == 200
    assert r.message == "done"
    assert r.data == [1, 2]


def test_resp_fail_defaults():
    r = Resp.fail(message="boom")
    assert r.code == 1
    assert r.message == "boom"
    assert r.data is None


def test_resp_fail_requires_message():
    with pytest.raises(TypeError):
        _bad(Resp.fail)()


def test_code_and_message_are_keyword_only():
    with pytest.raises(TypeError):
        _bad(Resp.ok)(200)


def test_classmethod_pair_returns_resp_instance():
    assert isinstance(Resp.ok(data=1), Resp)
    assert isinstance(Resp.fail(message="boom"), Resp)


def test_ok_fail_accept_code_override():
    assert Resp.ok(code=200).code == 200
    assert Resp.fail(code=404, message="not found").code == 404


def test_is_ok_property():
    assert Resp.ok().is_ok is True
    assert Resp().is_ok is True
    assert Resp.fail(message="boom").is_ok is False


def test_is_ok_follows_custom_code():
    assert Resp.ok(code=200).is_ok is False
    assert Resp.fail(code=0, message="约定俗成的成功码").is_ok is True


def test_data_validated_when_class_is_parameterized():
    with pytest.raises(ValidationError):
        Resp[int](data=_bad("abc"))
    with pytest.raises(ValidationError):
        Resp[int].ok(data=_bad("abc"))


def test_data_validated_on_model_validate_when_parameterized():
    with pytest.raises(ValidationError):
        Resp[int].model_validate({"data": "abc"})


def test_data_not_validated_when_class_is_not_parameterized():
    """已知限制：运行期拿不到 T，未参数化时 data 退化为 Any。

    需强校验时用 `Resp[Foo]`，或依赖 FastAPI 的 `response_model`。
    """
    assert Resp.ok(data="abc").data == "abc"
    assert Resp(data=object()).data is not None


def test_schema_marks_data_as_any_when_unparameterized():
    assert "type" not in Resp.model_json_schema()["properties"]["data"]
    assert Resp[int].model_json_schema()["properties"]["data"]["anyOf"][0] == {"type": "integer"}


def test_extra_fields_ignored():
    r = Resp(**_bad({"foo": 1}))
    assert "foo" not in r.model_dump()
    assert r == Resp()


def test_code_must_be_int_like():
    with pytest.raises(ValidationError):
        Resp(code=_bad("abc"))


def test_message_must_be_str():
    with pytest.raises(ValidationError):
        Resp(message=_bad(None))


def test_serialization():
    r = Resp(data={"a": 1})
    assert r.model_dump() == {"code": 0, "message": "success", "data": {"a": 1}}
    assert r.model_dump_json() == '{"code":0,"message":"success","data":{"a":1}}'


def test_is_ok_is_not_a_model_field():
    assert "is_ok" not in Resp.model_fields
    assert "is_ok" not in Resp.model_json_schema()["properties"]


def test_only_one_pair_of_entry_points_is_public():
    """构造入口只有 Resp.ok / Resp.fail 这一对，模块级同名函数是有意删除的。"""
    assert "ok" not in fdy.__all__
    assert "fail" not in fdy.__all__
    assert "ok" not in fdy.models.__all__
    assert not hasattr(fdy, "ok")
    assert not hasattr(fdy, "fail")
    assert not hasattr(fdy.models.resp, "ok")
    assert not hasattr(fdy.models.resp, "fail")
