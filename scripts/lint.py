"""Ruff 封装：check 只验证不改文件，fix 自动修复并格式化；范围覆盖 src/ tests/ scripts/

用法：uv run python -m scripts.lint [check|fix]（缺省为 check）
"""

import subprocess


def _run_ruff(*args: str) -> None:
    subprocess.run(["uv", "run", "ruff", *args], check=True)


def check() -> None:
    """检查：lint 规则 + 格式合规（只验证，不改文件）。"""
    _run_ruff("check", "src/", "tests/", "scripts/")
    _run_ruff("format", "--check", "src/", "tests/", "scripts/")


def fix() -> None:
    """修复：先自动修 lint 问题，再统一排版。"""
    _run_ruff("check", "--fix", "src/", "tests/", "scripts/")
    _run_ruff("format", "src/", "tests/", "scripts/")
