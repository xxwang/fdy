from typing import Any

import pytest
from pydantic import ValidationError

import fdy
from fdy import APIResponse


def _bad(value: Any) -> Any:
    """负例专用：擦除静态类型，让非法调用只在运行期暴露。"""
    return value


def test_fields_are_required():
    """code / message 是必填字段，默认值只由构造入口提供。"""
    with pytest.raises(ValidationError):
        _bad(APIResponse)()
    with pytest.raises(ValidationError):
        _bad(APIResponse)(code=0)


def test_success_defaults():
    r = APIResponse.success()
    assert r.code == 0
    assert r.message == "success"
    assert r.data is None


def test_success_overrides():
    r = APIResponse.success(code=200, message="done", data=[1, 2])
    assert r.code == 200
    assert r.message == "done"
    assert r.data == [1, 2]


def test_fail_defaults():
    r = APIResponse.fail()
    assert r.code == 1
    assert r.message == "fail"
    assert r.data is None


def test_entry_points_are_keyword_only():
    with pytest.raises(TypeError):
        _bad(APIResponse.success)(200)


def test_entry_points_return_instance():
    assert isinstance(APIResponse.success(data=1), APIResponse)
    assert isinstance(APIResponse.fail(message="boom"), APIResponse)


def test_entry_points_accept_code_override():
    assert APIResponse.success(code=200).code == 200
    assert APIResponse.fail(code=404, message="not found").code == 404


def test_default_messages_stay_in_the_signature():
    """默认文案写在构造入口的签名里，不作为模块常量对外导出。"""
    assert APIResponse.success().message == "success"
    assert APIResponse.fail().message == "fail"
    assert not hasattr(fdy.models.api_response, "_OK_MESSAGE")
    assert "OK_MESSAGE" not in fdy.__all__


def test_data_validated_when_class_is_parameterized():
    with pytest.raises(ValidationError):
        APIResponse[int](code=0, message="ok", data=_bad("abc"))
    with pytest.raises(ValidationError):
        APIResponse[int].success(data=_bad("abc"))


def test_data_validated_on_model_validate_when_parameterized():
    with pytest.raises(ValidationError):
        APIResponse[int].model_validate({"code": 0, "message": "ok", "data": "abc"})


def test_data_not_validated_when_class_is_not_parameterized():
    """已知限制：运行期拿不到 T，未参数化时 data 退化为 Any。

    需强校验时用 `APIResponse[Foo]`，或依赖 FastAPI 的 `response_model`。
    """
    assert APIResponse.success(data="abc").data == "abc"
    assert _bad(APIResponse)(code=0, message="ok", data=object()).data is not None


def test_schema_marks_data_as_any_when_unparameterized():
    assert "type" not in APIResponse.model_json_schema()["properties"]["data"]
    assert APIResponse[int].model_json_schema()["properties"]["data"]["anyOf"][0] == {
        "type": "integer"
    }


def test_extra_fields_ignored():
    r = _bad(APIResponse)(code=0, message="ok", foo=1)
    assert "foo" not in r.model_dump()


def test_code_must_be_int_like():
    with pytest.raises(ValidationError):
        APIResponse(code=_bad("abc"), message="ok")


def test_message_must_be_str():
    with pytest.raises(ValidationError):
        APIResponse(code=0, message=_bad(None))


def test_serialization():
    r = APIResponse.success(data={"a": 1})
    assert r.model_dump() == {"code": 0, "message": "success", "data": {"a": 1}}
    assert r.model_dump_json() == '{"code":0,"message":"success","data":{"a":1}}'


def test_only_one_pair_of_entry_points_is_public():
    """构造入口只有 APIResponse.success / .fail 这一对，模块级同名函数不存在。"""
    assert "success" not in fdy.__all__
    assert "fail" not in fdy.__all__
    assert "success" not in fdy.models.__all__
    assert not hasattr(fdy, "success")
    assert not hasattr(fdy, "fail")
    assert not hasattr(fdy.models.api_response, "success")
    assert not hasattr(fdy.models.api_response, "fail")
