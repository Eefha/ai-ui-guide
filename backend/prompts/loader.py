"""
提示词加载与渲染。

设计要点：
1. 统一 utf-8-sig 读取，避免 Windows 记事本写入的 BOM 混进 prompt 首字符；
2. 自己实现 $var 替换，不用 string.Template.safe_substitute —— 后者缺变量时会静默留空，
   导致线上出现「【用户之前的目标】空」这种难查的问题；这里缺变量直接报错；
3. 带缓存，改完文件可调 clear_cache() 热更新（开发时用）。
"""
import re
from pathlib import Path
from typing import Iterable

PROMPTS_DIR = Path(__file__).resolve().parent

_PLACEHOLDER_RE = re.compile(r"\$([a-zA-Z_][a-zA-Z0-9_]*)")
_cache: dict[str, str] = {}


class PromptError(RuntimeError):
    """提示词文件缺失或渲染失败。"""


def load_prompt(name: str) -> str:
    """读取提示词文件（不带 .txt 后缀名）。"""
    if name in _cache:
        return _cache[name]

    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise PromptError(f"提示词文件不存在：{path}")

    content = path.read_text(encoding="utf-8-sig").replace("\ufeff", "").strip()
    if not content:
        raise PromptError(f"提示词文件为空：{path}")

    _cache[name] = content
    return content


def placeholders(name: str) -> set[str]:
    """返回模板里声明的所有 $变量。"""
    return set(_PLACEHOLDER_RE.findall(load_prompt(name)))


def render_prompt(name: str, /, **kwargs) -> str:
    """
    渲染模板。传入的变量必须覆盖模板里的全部 $占位符，否则抛 PromptError。
    值允许是空字符串（由调用方决定要不要给空），但不允许漏传。
    """
    template = load_prompt(name)
    needed = set(_PLACEHOLDER_RE.findall(template))

    missing = needed - kwargs.keys()
    if missing:
        raise PromptError(
            f"渲染 {name} 缺少变量：{sorted(missing)}；模板需要：{sorted(needed)}"
        )

    def _sub(m: re.Match) -> str:
        value = kwargs[m.group(1)]
        return "" if value is None else str(value)

    return _PLACEHOLDER_RE.sub(_sub, template).strip()


def clear_cache():
    _cache.clear()


def list_prompts() -> list[str]:
    return sorted(p.stem for p in PROMPTS_DIR.glob("*.txt"))


def unused_placeholders(name: str, provided: Iterable[str]) -> set[str]:
    """调试用：模板没用到的多余变量。"""
    return set(provided) - placeholders(name)
