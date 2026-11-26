import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import get_collection, retrieve  # noqa: E402


async def main():
    # 1. 检查 Chroma 里有几个片段
    try:
        c = get_collection()
        print(f"[1] Chroma 片段数：{c.count()}")
    except Exception as e:
        print(f"[1] 检查失败：{e}")
        return

    # 2. 测多个查询
    queries = [
        "怎么新建 PyCharm 项目",
        "如何切换 Python 版本",
        "PyCharm 怎么用 Git",
    ]

    for q in queries:
        print("\n" + "=" * 60)
        print(f"[查询] {q}")
        results = await retrieve(q, top_k=3, min_score=0.3)
        if not results:
            print("  ⚠️ 没有检索到结果")
            continue
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] 来源：{r['source']}")
            print(f"      相似度：{r['score']}")
            print(f"      图片：{r['images']}")
            print(f"      内容：{r['content'][:120]}...")


if __name__ == "__main__":
    asyncio.run(main())