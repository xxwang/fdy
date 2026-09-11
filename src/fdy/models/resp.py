from typing import Any, cast

from pydantic import BaseModel, ConfigDict

OK_CODE = 0
FAIL_CODE = 1
_OK_MESSAGE = "success"  # 展示文案，非协议字段


class Resp[T](BaseModel):
    """统一响应结构 `{code, message, data}`"""

    code: int = OK_CODE
    message: str = _OK_MESSAGE
    data: T | None = None

    model_config = ConfigDict(extra="ignore")

    @property
    def is_ok(self) -> bool:
        """判断是否成功"""
        return self.code == OK_CODE

    @classmethod
    def ok[U = Any](
        cls, *, code: int = OK_CODE, message: str = _OK_MESSAGE, data: U | None = None
    ) -> Resp[U]:
        return cast(type[Resp[U]], cls)(code=code, message=message, data=data)

    @classmethod
    def fail[U = Any](
        cls, *, code: int = FAIL_CODE, message: str, data: U | None = None
    ) -> Resp[U]:
        return cast(type[Resp[U]], cls)(code=code, message=message, data=data)
