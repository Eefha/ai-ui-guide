"""
端到端冒烟测试：直接跑 Agent，不经过 HTTP 服务。

用法（在 backend 目录下）：
    .venv\\Scripts\\python.exe dev\\smoke_test.py
    .venv\\Scripts\\python.exe dev\\smoke_test.py 图片路径 "用户说的话"

它会打印每一轮的模板选择、耗时、模型给的坐标，方便调提示词时快速验证。
"""
import asyncio
import io
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from PIL import Image  # noqa: E402

from agent_graph import agent_graph  # noqa: E402
from llm_utils import prepare_image  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"


def load(path: Path):
    img = Image.open(path)
    img.load()
    b64, size = prepare_image(img)
    return b64, size, path.read_bytes()


async def run_case(name, image_name, message, history=None, goal=""):
    print("\n" + "=" * 70)
    print(f"[{name}] 图={image_name or '无'} 话={message or '（空）'}")

    state = {
        "session_id": "smoke",
        "user_message": message,
        "img_b64": None,
        "img_size": None,
        "img_bytes": None,
        "mode": "",
        "force_new": False,
        "image_is_fresh": True,
        "goal": goal,
        "history": history or [],
        "retry_count": 0,
        "error": "",
    }
    if image_name:
        b64, size, raw = load(ASSETS / image_name)
        state.update({"img_b64": b64, "img_size": size, "img_bytes": raw})

    started = time.time()
    final = await agent_graph.ainvoke(state)
    cost = time.time() - started

    r = final.get("result") or {}
    print(f"  模板      : {final.get('template')}")
    print(f"  耗时      : {cost:.1f}s")
    print(f"  reply_type: {r.get('reply_type')}  bbox_valid={r.get('bbox_valid')}")
    print(f"  target    : {r.get('target')!r}")
    print(f"  bbox      : {r.get('bbox')}  {r.get('bbox_error') or ''}")
    print(f"  action    : {r.get('action')!r}")
    print(f"  text      : {(r.get('text_reply') or '')[:160]}")
    print(f"  置信度    : {r.get('confidence')}")
    print(f"  OCR/RAG/联网: {(final.get('ocr_debug') or {}).get('count')} / "
          f"{(final.get('rag_debug') or {}).get('count')} / "
          f"{(final.get('web_debug') or {}).get('count')}")
    return final


async def main():
    if len(sys.argv) >= 3:
        await run_case("自定义", sys.argv[1], sys.argv[2])
        return

    # 1. 有截图 + 明确操作目标 → 期望 action
    await run_case("定位-浏览器", "图片2.png", "我想搜索商品")

    # 2. 有截图 + 提问 → 期望 text
    await run_case("提问-浏览器", "图片2.png", "这个界面是干什么的")

    # 3. 有截图 + 没说话 → 期望 text（反问）
    await run_case("只发图", "图片2.png", "")

    # 4. 纯文字 → 期望 text
    await run_case("纯文字", None, "PyCharm 怎么切换 Python 解释器")

    # 5. 多步任务第二步 → 期望 action，且不重复第一步
    await run_case(
        "多步续接", "图片1.png", "然后呢",
        goal="在编辑器里打开终端", history=[{"action": "点击底部『终端』标签", "bbox": [0.03, 0.93, 0.05, 0.03],
                                              "target": "终端标签"}],
    )


if __name__ == "__main__":
    asyncio.run(main())
