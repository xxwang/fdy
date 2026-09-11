"""fdy —— 日常开发工具库。"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version

from . import models, utils
from .models import FAIL_CODE, OK_CODE, Resp
from .utils import *  # noqa: F403

try:
    __version__ = _package_version("fdy")
except PackageNotFoundError:  # 源码目录未安装时兜底
    __version__ = "0.0.0"

__all__ = [
    *utils.__all__,
    "FAIL_CODE",
    "OK_CODE",
    "Resp",
    "__version__",
    "models",
    "utils",
]
