"""
独立的百度搜索 API 测试脚本
不依赖项目其他代码，只测试 API 能否调通
"""
import os
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH, override=True)

BAIDU_SEARCH_API_KEY = os.environ.get("BAIDU_SEARCH_API_KEY")
BAIDU_SEARCH_URL = "https://qianfan.baidubce.com/v2/ai_search/web_search"


async def test_search(query: str):
    print("=" * 60)
    print(f"查询：{query}")
    print("=" * 60)

    # 1. 检查 Key
    print(f"\n[1] API Key 状态：")
    if not BAIDU_SEARCH_API_KEY:
        print("    ❌ 未配置 BAIDU_SEARCH_API_KEY")
        print("    请在 backend/.env 里加一行：")
        print("    BAIDU_SEARCH_API_KEY=bce-v3/ALTAK-你的Key")
        return

    key_preview = BAIDU_SEARCH_API_KEY[:20] + "..." if len(BAIDU_SEARCH_API_KEY) > 20 else BAIDU_SEARCH_API_KEY
    print(f"    ✅ 已配置：{key_preview}")
    print(f"    Key 长度：{len(BAIDU_SEARCH_API_KEY)}")

    # 2. 组装请求
    headers = {
        "Authorization": f"Bearer {BAIDU_SEARCH_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [{"content": query, "role": "user"}],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": 5}],
        "query_policy": {"enable_rewrite": True},
    }

    print(f"\n[2] 请求 URL：{BAIDU_SEARCH_URL}")
    print(f"    Payload：{payload}")

    # 3. 发起请求
    print(f"\n[3] 调用 API...")
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(BAIDU_SEARCH_URL, headers=headers, json=payload)

        print(f"    HTTP 状态码：{resp.status_code}")

        if resp.status_code != 200:
            print(f"    ❌ 请求失败")
            print(f"    响应内容：{resp.text[:500]}")
            return

        # 4. 解析结果
        data = resp.json()
        print(f"\n[4] 响应结构：")
        print(f"    顶层字段：{list(data.keys())}")

        references = data.get("references", [])
        if not references:
            references = data.get("data", {}).get("references", [])

        print(f"\n[5] 搜索结果（共 {len(references)} 条）：")
        if not references:
            print("    ⚠️ 没有 references 字段")
            import json
            print(f"    完整响应：{json.dumps(data, ensure_ascii=False, indent=2)[:800]}")
            return

        for i, ref in enumerate(references[:5], 1):
            print(f"\n    [{i}] 标题：{ref.get('title', '(无)')}")
            print(f"        来源：{ref.get('website', '') or ref.get('web_anchor', '(无)')}")
            content = ref.get('content', '') or ref.get('snippet', '')
            print(f"        摘要：{content[:100]}...")
            print(f"        链接：{ref.get('url', '(无)')}")

        print("\n" + "=" * 60)
        print("✅ 百度搜索 API 正常工作！")
        print("=" * 60)

    except httpx.TimeoutException:
        print("    ❌ 请求超时（20秒）")
    except Exception as e:
        print(f"    ❌ 异常：{type(e).__name__}: {e}")


async def main():
    queries = [
        "WPS 怎么导出 PDF",
        "PyCharm 新建项目",
    ]
    for q in queries:
        await test_search(q)
        print("\n\n")


if __name__ == "__main__":
    asyncio.run(main())