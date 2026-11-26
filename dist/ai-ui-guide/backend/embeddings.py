import math
import httpx
from typing import List, Optional

import config

DASHSCOPE_API_KEY = config.DASHSCOPE_API_KEY
EMBED_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
EMBED_MODEL = "text-embedding-v3"
MAX_TEXT_LEN = 2000

# 简单缓存，避免重复计算
_cache: dict = {}


async def get_embedding(text: str) -> Optional[List[float]]:
    """调用阿里云 embedding API，返回向量"""
    if not text or not DASHSCOPE_API_KEY:
        return None

    text = (text or "").strip()[:MAX_TEXT_LEN]
    if not text:
        return None
    if text in _cache:
        return _cache[text]

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": EMBED_MODEL,
        "input": [text],
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(EMBED_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        vec = data["data"][0]["embedding"]
        if len(_cache) >= 512:
            _cache.clear()  # 简单防泄漏，别让它无限长
        _cache[text] = vec
        return vec
    except Exception as e:
        print(f"[embedding] 调用失败：{e}")
        return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """余弦相似度，范围 -1 到 1"""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def semantic_similarity(text1: str, text2: str) -> Optional[float]:
    """计算两段文本的语义相似度"""
    if not text1 or not text2:
        return None
    v1 = await get_embedding(text1)
    v2 = await get_embedding(text2)
    if v1 is None or v2 is None:
        return None
    return cosine_similarity(v1, v2)