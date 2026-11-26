"""
百度搜索 API 封装
- web_search：原始搜索
- web_search_and_filter：搜索 + embedding 相似度过滤
"""
import httpx
from typing import List

import config

BAIDU_SEARCH_API_KEY = config.BAIDU_SEARCH_API_KEY
BAIDU_SEARCH_URL = "https://qianfan.baidubce.com/v2/ai_search/web_search"

# 相关性阈值：0.8 在中文短 query 上几乎筛掉所有结果，实测 0.5~0.6 比较合理
WEB_RELEVANCE_THRESHOLD = config.WEB_MIN_SCORE


async def web_search(query: str, top_k: int = 8) -> List[dict]:
    """
    调用百度搜索 API（原始结果）
    注意：top_k 提到 8，因为过滤会丢弃一部分，多取一些补偿
    """
    if not BAIDU_SEARCH_API_KEY:
        print("[web_search] BAIDU_SEARCH_API_KEY 未配置，跳过搜索")
        return []

    if len(query) > 72:
        query = query[:72]

    headers = {
        "Authorization": f"Bearer {BAIDU_SEARCH_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [{"content": query, "role": "user"}],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": top_k}],
        "query_policy": {"enable_rewrite": True},
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(BAIDU_SEARCH_URL, headers=headers, json=payload)

        if resp.status_code != 200:
            print(f"[web_search] 请求失败：{resp.status_code} {resp.text[:200]}")
            return []

        data = resp.json()
        references = data.get("references", [])
        if not references:
            references = data.get("data", {}).get("references", [])

        results = []
        for ref in references:
            results.append({
                "title": ref.get("title", ""),
                "content": ref.get("content", "") or ref.get("snippet", ""),
                "url": ref.get("url", ""),
                "date": ref.get("date", ""),
                "site": ref.get("website", "") or ref.get("web_anchor", ""),
            })

        print(f"[web_search] 检索到 {len(results)} 条原始结果")
        return results

    except httpx.TimeoutException:
        print("[web_search] 请求超时")
        return []
    except Exception as e:
        print(f"[web_search] 异常：{e}")
        return []


async def web_search_and_filter(
    query: str,
    top_k: int = 8,
    min_score: float = WEB_RELEVANCE_THRESHOLD,
) -> List[dict]:
    """
    搜索 + 过滤：
    1. 调百度搜索拿 top_k 条结果
    2. 用 embedding 计算每条结果和 query 的相似度
    3. 过滤低于 min_score 的结果
    4. 按相似度降序排序
    """
    # 1. 原始搜索
    raw_results = await web_search(query, top_k=top_k)
    if not raw_results:
        return []

    # 2. 拿 query 的 embedding
    try:
        from embeddings import get_embedding, cosine_similarity
    except ImportError:
        print("[web_search] embeddings 模块不可用，跳过过滤")
        return raw_results

    q_emb = await get_embedding(query)
    if q_emb is None:
        print("[web_search] query embedding 失败，跳过过滤")
        return raw_results

    # 3. 逐条计算相似度
    filtered = []
    for r in raw_results:
        text = f"{r.get('title', '')} {r.get('content', '')[:300]}"
        if not text.strip():
            continue

        emb = await get_embedding(text)
        if emb is None:
            continue

        score = cosine_similarity(q_emb, emb)
        r["relevance"] = round(score, 3)

        if score >= min_score:
            filtered.append(r)
        else:
            print(f"[web_search] 过滤低相关：{r.get('title', '')[:40]} (相似度 {score:.3f})")

    # 4. 按相似度降序
    filtered.sort(key=lambda x: -x.get("relevance", 0))

    print(f"[web_search] 过滤后保留 {len(filtered)}/{len(raw_results)} 条结果")
    return filtered


def format_web_results(results: List[dict], max_items: int = 5) -> str:
    """格式化成给模型看的文本"""
    if not results:
        return "（未检索到网络结果）"

    parts = []
    for i, r in enumerate(results[:max_items], 1):
        title = r.get("title", "")
        content = r.get("content", "")[:600]
        site = r.get("site", "")
        score = r.get("relevance", "")
        score_str = f"（相关性 {score}）" if score else ""
        parts.append(f"【网络结果 {i}】{title}（来源：{site}）{score_str}\n{content}")

    return "\n\n".join(parts)


if __name__ == "__main__":
    import asyncio
    async def main():
        print("=== 原始搜索 ===")
        r1 = await web_search("WPS 怎么导出 PDF", top_k=8)
        print(f"原始：{len(r1)} 条")
        print("\n\n=== 过滤后（阈值 0.8）===")
        r2 = await web_search_and_filter("WPS 怎么导出 PDF", top_k=8)
        print(format_web_results(r2))
    asyncio.run(main())