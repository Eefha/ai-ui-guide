"""
模型调用与响应解析。

只做三件事：图片编码、调大模型、把返回内容解析成 dict。
提示词组装在 prompt_builder.py，坐标校验在 bbox.py，不要再混进来。
"""
import base64
import io
import json
import re
from typing import Optional, Tuple

import httpx
from PIL import Image

import config

DASHSCOPE_API_KEY = config.DASHSCOPE_API_KEY
MODEL_NAME = config.MODEL_NAME
API_URL = config.API_URL


# ============ 图片 ============
def prepare_image(img: Image.Image) -> Tuple[str, Tuple[int, int]]:
    """
    统一压缩成 JPEG 并返回 (base64, (宽, 高))。
    返回的尺寸就是模型看到的尺寸，像素坐标回退换算要用它。
    """
    if img.mode != "RGB":
        img = img.convert("RGB")

    if config.IMAGE_MAX_SIDE and max(img.size) > config.IMAGE_MAX_SIDE:
        ratio = config.IMAGE_MAX_SIDE / max(img.size)
        img = img.resize(
            (max(1, int(img.width * ratio)), max(1, int(img.height * ratio))),
            Image.LANCZOS,
        )

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=config.IMAGE_JPEG_QUALITY, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8"), img.size


def image_to_base64(img: Image.Image) -> str:
    """兼容旧调用，只需要 base64 时用。"""
    return prepare_image(img)[0]


# ============ 解析 ============
_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*(.*?)\s*```", re.DOTALL)
_THINK_RE = re.compile(r"<(?:think|thinking|reasoning)>.*?</(?:think|thinking|reasoning)>", re.DOTALL | re.IGNORECASE)


def parse_json_from_text(text: str) -> dict:
    """从模型输出里抠出第一个 JSON 对象。容忍代码块、思考标签、前后废话、尾逗号。"""
    if not text:
        raise ValueError("模型返回为空")

    text = _THINK_RE.sub("", text).strip()

    fenced = _FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"找不到 JSON 对象：{text[:120]}")

    body = text[start:end + 1]

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        pass

    # 常见小毛病：尾逗号、中文引号
    repaired = re.sub(r",\s*([}\]])", r"\1", body)
    repaired = repaired.replace("“", '"').replace("”", '"').replace("，", ",").replace("：", ":")
    try:
        return json.loads(repaired)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败（{e}）：{body[:160]}") from e


def safe_parse(content: str) -> dict:
    """解析失败返回 {}，由调用方决定降级策略。"""
    try:
        data = parse_json_from_text(content)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"[llm] 解析失败：{e}")
        return {}


# ============ 调用 ============
class ModelError(RuntimeError):
    pass


async def call_model(
    system: str,
    user_text: str,
    img_b64: Optional[str] = None,
    temperature: Optional[float] = None,
    max_attempts: Optional[int] = None,
) -> str:
    if not DASHSCOPE_API_KEY:
        raise ModelError("未配置 DASHSCOPE_API_KEY")

    content = [{"type": "text", "text": user_text}]
    if img_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
        })

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
        "temperature": config.LLM_TEMPERATURE if temperature is None else temperature,
    }
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    attempts = max_attempts or config.LLM_MAX_ATTEMPTS
    last_error = ""

    for i in range(max(1, attempts)):
        try:
            async with httpx.AsyncClient(timeout=config.LLM_TIMEOUT) as client:
                resp = await client.post(API_URL, headers=headers, json=payload)
        except httpx.TimeoutException:
            last_error = f"模型请求超时（{config.LLM_TIMEOUT}s）"
            print(f"[llm] {last_error}")
            continue
        except httpx.HTTPError as e:
            last_error = f"网络错误：{e}"
            print(f"[llm] {last_error}")
            continue

        if resp.status_code == 200:
            try:
                message = resp.json()["choices"][0]["message"]
            except (KeyError, IndexError, ValueError) as e:
                raise ModelError(f"响应结构异常：{e}") from e
            text = (message.get("content") or "").strip()
            if not text:
                raise ModelError("模型返回了空内容")
            return text

        # 429 / 5xx 值得重试，其余直接报错
        body = resp.text[:300]
        last_error = f"HTTP {resp.status_code}：{body}"
        print(f"[llm] {last_error}")
        if resp.status_code not in (429, 500, 502, 503, 504):
            raise ModelError(last_error)

    raise ModelError(f"模型调用失败（已重试 {attempts} 次）：{last_error}")
