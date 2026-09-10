# fdy

日常开发工具库 —— 8 个模块、73 个公开符号，`import fdy` 开箱即用。

## 安装

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

fdy.snake_case("HTTPServerConfig")                # 'http_server_config'
fdy.mask("13812345678", 3, 4)                     # '138****5678'
fdy.human_size(1536)                              # '1.5 KB'
fdy.humanize_delta(-7200)                         # '2 小时后'
fdy.deep_get({"a": {"b": [1, 2, 3]}}, "a.b.2")    # 3
list(fdy.chunk([1, 2, 3, 4, 5], 2))               # [[1, 2], [3, 4], [5]]
fdy.group_by(["a", "bb", "cc"], len)              # {1: ['a'], 2: ['bb', 'cc']}
```

## 模块一览

| 模块 | 用途 | 主要函数 |
| --- | --- | --- |
| `strings` | 命名风格转换、清洗、脱敏 | `camel_case` `pascal_case` `snake_case` `kebab_case` `slugify` `truncate` `mask` `normalize_space` `random_string` |
| `containers` | 嵌套结构操作与集合处理 | `deep_merge` `deep_get` `deep_set` `flatten` `chunk` `group_by` `unique` `unique_by` `pick` `omit` `invert` `first` `last` |
| `checks` | 容错类型转换与判断 | `to_bool` `to_int` `to_float` `safe_cast` `is_empty` `is_blank` `is_iterable` `ensure_list` |
| `ids` | ID 与随机串生成 | `uuid_str` `short_id` `token_hex` `token_urlsafe` `is_valid_uuid` |
| `dates` | 时间解析、格式化与区间计算 | `parse_datetime` `format_datetime` `humanize_delta` `date_range` `days_between` `start_of_day` `end_of_day` `start_of_month` `now` `to_timestamp` `from_timestamp` |
| `files` | 文件读写与路径处理 | `read_text` `write_text` `read_json` `write_json` `iter_files` `ensure_dir` `human_size` `safe_filename` `unique_path` `file_hash` |
| `decorators` | 常用函数式装饰器 | `timer` `retry` `memoize` `silent` `singleton` |
| `http_client` | 基于 httpx 的请求封装（需 `fdy[http]`） | `HttpClient` `get_json` `post_json` |

所有函数都在顶层重导出，`import fdy` 后直接 `fdy.函数名(...)` 调用；也可以按模块导入，如 `from fdy import strings`。

## 设计说明

- **零运行时依赖**：除可选的 `http_client` 外全部基于标准库。
- **延迟导入 httpx**：`http_client` 在函数内部导入 httpx，保证未安装 httpx 时 `import fdy` 不失败。
- **Python 3.12+**：泛型使用 PEP 695 语法，如 `def chunk[T](...)`。
- **模块命名避开标准库**：用 `containers` / `checks` / `dates`，避免与 `collections` / `types` / `datetime` 混淆。
- `chunk` 返回生成器，按需迭代；需要列表时用 `list(...)` 包裹。

## 开发

```bash
uv sync                                # 安装依赖
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
