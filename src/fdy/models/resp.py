from pydantic import BaseModel, ConfigDict

OK_CODE = 0
FAIL_CODE = 1
_OK_MESSAGE = "success"  # 展示文案，非协议字段


class Resp[T](BaseModel):
    """统一响应结构 `{code, message, data}`。

    `data` 的类型校验只在显式参数化时生效（`Resp[Foo](...)`）；
    未参数化时退化为 `Any`，不做校验。
    """

    model_config = ConfigDict(extra="ignore")

    code: int = OK_CODE
    message: str = _OK_MESSAGE
    data: T | None = None

    @property
    def is_ok(self) -> bool:
        return self.code == OK_CODE

    @classmethod
    def ok(
        cls, *, code: int = OK_CODE, message: str = _OK_MESSAGE, data: T | None = None
    ) -> Resp[T]:
        return cls(code=code, message=message, data=data)

    @classmethod
    def fail(cls, *, code: int = FAIL_CODE, message: str, data: T | None = None) -> Resp[T]:
        """message 必填，强制说明失败原因。"""
        return cls(code=code, message=message, data=data)
