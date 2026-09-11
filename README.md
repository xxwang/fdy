# fdy

日常开发工具库 —— 9 个模块、78 个公开符号，`import fdy` 开箱即用。

## 安装

需要 Python 3.14 及以上。

```bash
pip install fdy
```

`http_client` 模块基于 httpx，作为可选依赖提供：

```bash
pip install "fdy[http]"
```

未安装 httpx 时 `import fdy` 照常可用，只有实际调用 `http_client` 时才会提示缺依赖。

## 快速开始

```python
import fdy

fdy.snake_case("HTTPServerConfig")  # 'http_server_config'
fdy.mask("13812345678", 3, 4)  # '138****5678'
fdy.human_size(1536)  # '1.5 KB'
fdy.humanize_delta(-7200)  # '2 小时后'
fdy.deep_get({"a": {"b": [1, 2, 3]}}, "a.b.2")  # 3
list(fdy.chunk([1, 2, 3, 4, 5], 2))  # [[1, 2], [3, 4], [5]]
fdy.group_by(["a", "bb", "cc"], len)  # {1: ['a'], 2: ['bb', 'cc']}
```

统一响应模型：

```python
from fdy import FAIL_CODE, Resp

Resp.ok(data={"id": 1})  # Resp(code=0, message='success', data={'id': 1})
Resp.fail(message="参数错误")  # Resp(code=1, message='参数错误', data=None)

Resp.fail(message="参数错误").is_ok  # False
Resp.fail(message="参数错误").code == FAIL_CODE  # True
```

## 模块一览

工具函数位于 `fdy.utils` 子包，数据模型位于 `fdy.models`：

| 模块 | 用途 | 主要函数 |
| --- | --- | --- |
| `utils.strings` | 命名风格转换、清洗、脱敏 | `camel_case` `pascal_case` `snake_case` `kebab_case` `slugify` `truncate` `mask` `normalize_space` `random_string` |
| `utils.containers` | 嵌套结构操作与集合处理 | `deep_merge` `deep_get` `deep_set` `flatten` `chunk` `group_by` `unique` `unique_by` `pick` `omit` `invert` `first` `last` |
| `utils.checks` | 容错类型转换与判断 | `to_bool` `to_int` `to_float` `safe_cast` `is_empty` `is_blank` `is_iterable` `ensure_list` |
| `utils.ids` | ID 与随机串生成 | `uuid_str` `short_id` `token_hex` `token_urlsafe` `is_valid_uuid` |
| `utils.dates` | 时间解析、格式化与区间计算 | `parse_datetime` `format_datetime` `humanize_delta` `date_range` `days_between` `start_of_day` `end_of_day` `start_of_month` `now` `to_timestamp` `from_timestamp` |
| `utils.files` | 文件读写与路径处理 | `read_text` `write_text` `read_json` `write_json` `iter_files` `ensure_dir` `human_size` `safe_filename` `unique_path` `file_hash` |
| `utils.decorators` | 常用函数式装饰器 | `timer` `retry` `memoize` `silent` `singleton` |
| `utils.http_client` | 基于 httpx 的请求封装（需 `fdy[http]`） | `HttpClient` `get_json` `post_json` |
| `models.resp` | 统一响应结构 `{code, message, data}` | `Resp`（`Resp.ok` / `Resp.fail`）`OK_CODE` `FAIL_CODE` |

所有符号都在顶层重导出，`import fdy` 后直接 `fdy.函数名(...)` 调用；也可以按模块导入，如 `from fdy import strings`、`from fdy import Resp`。

## 设计说明

- **仅一个运行时依赖**：`pydantic`（用于 `models`）。`http_client` 所需的 httpx 走可选依赖 `fdy[http]`，其余全部基于标准库。
- **延迟导入 httpx**：`http_client` 在函数内部导入 httpx，保证未安装 httpx 时 `import fdy` 不失败。
- **`Resp` 只有一对构造入口**：成功 `Resp.ok(...)`、失败 `Resp.fail(...)`（`message` 必填，避免把失败写成 `code=0` 的成功响应）。不额外提供模块级 `ok` / `fail` 函数，免得把 `ok` / `fail` 这类通用名注入调用方命名空间。
- **常量只导出协议字段**：`OK_CODE` / `FAIL_CODE` 是机器判断的协议值，可 `from fdy import FAIL_CODE` 直接比较；`Resp.message` 的默认值 `"success"` 是展示文案、随时可能改措辞，因此只作模块内部默认值，不导出。
- **`Resp.data` 的类型校验需显式参数化**：Python 泛型在运行期拿不到 `T`，`Resp.ok(data=...)` 不会校验 `data`（JSON schema 里 `data` 为 `Any`）；要强校验应写 `Resp[Foo](data=...)` 或 `Resp[Foo].ok(data=...)`，FastAPI 场景由 `response_model=Resp[Foo]` 兜住。
- **Python 3.14+**：依赖 3.14 的三项语言特性 —— PEP 695（`class Resp[T]`、`def chunk[T](...)` 泛型语法）、PEP 649（注解延迟求值）、PEP 758（`except A, B:` 可省略括号）。
- **模块命名避开标准库**：用 `containers` / `checks` / `dates`，避免与 `collections` / `types` / `datetime` 混淆。
- `chunk` 返回生成器，按需迭代；需要列表时用 `list(...)` 包裹。

## 开发

```bash
uv sync                                # 安装依赖（含 dev 组）
uv run pytest                          # 运行测试
uv run ruff check src tests scripts    # 静态检查
uv run ruff format --check src tests   # 格式检查
```

或使用封装脚本：

```bash
uv run python -m scripts.lint          # 检查（等价于上面两条）
uv run python -m scripts.lint fix      # 自动修复 + 格式化
```

## License

MIT
