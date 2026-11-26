"""
LangGraph 编排。

    check_task → gather_context → call_model → validate ─┬→ retry ─┐
                       (OCR+RAG 并发)                     │         │
                                                          └→ finalize → END
                                                                ↑
                                                     (retry 走完再回 validate)

相比旧版的改动：
- 用户输入不再丢失（模板问题在 prompt_builder 里修好了）
- OCR 与 RAG 并发，联网搜索只在 RAG 没命中时才发
- 只有「要圈位置」的回复才会重试；纯文字回答不再被逼着编坐标
- 重试仍失败时降级为文字回答，而不是给前端一个空框
"""
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

import config
from bbox import normalize_bbox
from llm_utils import call_model, safe_parse
from prompt_builder import build_messages, build_retry_messages

MAX_RETRIES = 1
NEW_TASK_KEYWORDS = [
    "新任务", "换个问题", "换一个问题", "另一个问题", "重新开始", "重来",
    "换个目标", "新的目标", "切换到另一个",
]


class AgentState(TypedDict, total=False):
    session_id: str
    user_message: str
    img_b64: Optional[str]
    img_size: Optional[tuple]
    img_bytes: Optional[bytes]
    mode: str
    force_new: bool
    image_is_fresh: bool

    goal: str
    history: list

    is_new_task: bool
    new_task_reason: Optional[str]

    ocr_text: str
    ocr_debug: dict
    rag_text: str
    rag_debug: dict
    rag_hit: bool
    web_text: str
    web_debug: dict

    template: str
    result: dict
    retry_count: int
    error: str


def _empty_ocr():
    return {"enabled": False, "count": 0, "samples": [], "elements": [], "error": ""}


def _empty_rag():
    return {"enabled": False, "count": 0, "samples": [], "error": ""}


def _empty_web():
    return {"enabled": False, "count": 0, "samples": [], "error": ""}


# ============ 1. 判断是否新任务 ============
def detect_new_task_by_keyword(text: str) -> bool:
    if not text:
        return False
    t = text.replace(" ", "")
    return any(kw in t for kw in NEW_TASK_KEYWORDS)


async def _semantic_similarity(a: str, b: str) -> Optional[float]:
    try:
        from embeddings import semantic_similarity
        return await semantic_similarity(a, b)
    except Exception as e:
        print(f"[agent] 相似度检测失败：{e}")
        return None


async def node_check_task(state: AgentState) -> AgentState:
    text = (state.get("user_message") or "").strip()
    goal = (state.get("goal") or "").strip()

    reason = None
    if state.get("force_new"):
        reason = "force"
    elif not goal:
        reason = "first"
    elif text and detect_new_task_by_keyword(text):
        reason = "keyword"
    elif text and len(text) >= 8:
        sim = await _semantic_similarity(goal, text)
        if sim is not None:
            print(f"[agent] 目标相似度 {sim:.3f}")
            if sim < config.SIMILARITY_THRESHOLD:
                reason = "similarity"

    if reason:
        print(f"[agent] 新任务（{reason}）")
        state["is_new_task"] = True
        state["new_task_reason"] = reason
        if reason != "first":
            state["goal"] = ""
            state["history"] = []
    else:
        state["is_new_task"] = False
        state["new_task_reason"] = None

    state["history"] = (state.get("history") or [])[-config.MAX_HISTORY_STEPS:]
    return state


# ============ 2. 收集上下文（OCR / RAG / 联网） ============
async def _run_ocr(state: AgentState) -> None:
    if not state.get("img_bytes") or not config.ENABLE_OCR:
        state["ocr_text"] = "（OCR 未启用）"
        state["ocr_debug"] = _empty_ocr()
        return

    try:
        import asyncio
        import io

        from PIL import Image

        from ocr import extract_text_elements, format_candidates_for_prompt

        img = Image.open(io.BytesIO(state["img_bytes"]))
        # SDK 是同步的，丢到线程里跑，别把事件循环堵住
        elements = await asyncio.to_thread(extract_text_elements, img)
        state["ocr_text"] = format_candidates_for_prompt(elements, max_items=config.OCR_MAX_ITEMS)
        state["ocr_debug"] = {
            "enabled": True,
            "count": len(elements),
            "samples": [
                {"content": e["content"], "confidence": e["confidence"]}
                for e in elements[:8]
            ],
            "elements": elements[:100],
            "error": "",
        }
        print(f"[agent] OCR：{len(elements)} 个文字")
    except Exception as e:
        print(f"[agent] OCR 失败：{e}")
        state["ocr_text"] = f"（OCR 失败：{str(e)[:100]}）"
        state["ocr_debug"] = {**_empty_ocr(), "enabled": True, "error": str(e)[:200]}


async def _run_rag(state: AgentState, query: str) -> None:
    if not config.ENABLE_RAG or not query:
        state["rag_text"] = "（未检索到有效内容）"
        state["rag_debug"] = _empty_rag()
        state["rag_hit"] = False
        return

    try:
        from rag import format_rag_context, retrieve_relevant

        results = await retrieve_relevant(query, top_k=config.RAG_TOP_K)
        state["rag_text"] = format_rag_context(results)
        state["rag_hit"] = bool(results)
        state["rag_debug"] = {
            "enabled": True,
            "count": len(results),
            "samples": [
                {
                    "source": r["source"],
                    "score": r["score"],
                    "preview": r["content"][:150],
                    "images": r.get("images", []),
                }
                for r in results
            ],
            "error": "",
        }
        print(f"[agent] RAG：{len(results)} 个片段")
    except Exception as e:
        print(f"[agent] RAG 失败：{e}")
        state["rag_text"] = "（未检索到有效内容）"
        state["rag_hit"] = False
        state["rag_debug"] = {**_empty_rag(), "enabled": True, "error": str(e)[:200]}


async def _run_web(state: AgentState, query: str) -> None:
    has_image = bool(state.get("img_b64"))
    skip_reason = ""

    if not config.ENABLE_WEB_SEARCH:
        skip_reason = "已关闭"
    elif not query:
        skip_reason = "没有可搜索的内容"
    elif state.get("rag_hit"):
        skip_reason = "本地知识库已命中"
    elif has_image and not config.WEB_SEARCH_WITH_IMAGE:
        skip_reason = "带截图时不联网"

    if skip_reason:
        state["web_text"] = "（未进行网络搜索）"
        state["web_debug"] = {**_empty_web(), "skip_reason": skip_reason}
        return

    try:
        from web_search import format_web_results, web_search_and_filter

        results = await web_search_and_filter(query, top_k=config.WEB_TOP_K)
        state["web_text"] = format_web_results(results)
        state["web_debug"] = {
            "enabled": True,
            "count": len(results),
            "samples": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "site": r.get("site", ""),
                    "relevance": r.get("relevance", 0),
                    "preview": (r.get("content", "") or "")[:150],
                }
                for r in results
            ],
            "error": "",
        }
        print(f"[agent] 联网：{len(results)} 条")
    except Exception as e:
        print(f"[agent] 联网失败：{e}")
        state["web_text"] = "（网络搜索失败）"
        state["web_debug"] = {**_empty_web(), "enabled": True, "error": str(e)[:200]}


async def node_gather_context(state: AgentState) -> AgentState:
    import asyncio
    import time

    query = " ".join(
        p for p in [(state.get("goal") or "").strip(), (state.get("user_message") or "").strip()] if p
    ).strip()

    t0 = time.perf_counter()
    # OCR 与向量检索互不依赖，并发跑
    await asyncio.gather(_run_ocr(state), _run_rag(state, query))
    t1 = time.perf_counter()

    await _run_web(state, query)
    t2 = time.perf_counter()

    print(f"[agent] 耗时：OCR+RAG {t1 - t0:.1f}s，联网 {t2 - t1:.1f}s")
    return state


# ============ 3. 调模型 ============
async def node_call_model(state: AgentState) -> AgentState:
    messages = build_messages(
        goal=state.get("goal", ""),
        history=state.get("history", []),
        user_message=state.get("user_message", ""),
        has_image=bool(state.get("img_b64")),
        image_size=state.get("img_size"),
        image_is_fresh=state.get("image_is_fresh", True),
        ocr_text=state.get("ocr_text", ""),
        rag_text=state.get("rag_text", ""),
        web_text=state.get("web_text", ""),
    )
    state["template"] = messages["template"]
    print(f"[agent] 模板 {messages['template']}，图片 {'有' if state.get('img_b64') else '无'}")

    try:
        import time

        t0 = time.perf_counter()
        content = await call_model(messages["system"], messages["user"], state.get("img_b64"))
        state["result"] = safe_parse(content) or {"_raw": content[:500]}
        preview = state["result"].get("action") or state["result"].get("text_reply") or ""
        print(f"[agent] 模型 {(time.perf_counter() - t0):.1f}s：{(preview or '(空)')[:60]}")
    except Exception as e:
        print(f"[agent] 模型调用失败：{e}")
        state["result"] = {}
        state["error"] = str(e)

    return state


# ============ 4. 校验 ============
async def node_validate(state: AgentState) -> AgentState:
    result = dict(state.get("result") or {})
    has_image = bool(state.get("img_b64"))

    reply_type = str(result.get("reply_type") or "").strip().lower()
    if reply_type not in ("action", "text"):
        # 模型没给或给错：有图且给了 action 描述就当 action，否则 text
        reply_type = "action" if (has_image and result.get("action")) else "text"
    if not has_image:
        reply_type = "text"

    result["reply_type"] = reply_type
    result["target"] = str(result.get("target") or "").strip()
    result["action"] = str(result.get("action") or "").strip()
    result["text_reply"] = str(result.get("text_reply") or "").strip()
    result["explanation"] = str(result.get("explanation") or "").strip()

    try:
        result["confidence"] = round(min(1.0, max(0.0, float(result.get("confidence", 0)))), 3)
    except (TypeError, ValueError):
        result["confidence"] = 0.0

    if reply_type == "action":
        bbox, reason = normalize_bbox(result.get("bbox"), state.get("img_size"))
        if bbox:
            result["bbox"] = bbox
            result["bbox_valid"] = True
            print(f"[agent] bbox 有效 {bbox}")
        else:
            result["bbox"] = [0, 0, 0, 0]
            result["bbox_valid"] = False
            result["bbox_error"] = reason
            print(f"[agent] bbox 无效：{reason}")
    else:
        result["bbox"] = [0, 0, 0, 0]
        result["bbox_valid"] = False

    state["result"] = result
    return state


# ============ 5. 重试 ============
async def node_retry(state: AgentState) -> AgentState:
    state["retry_count"] = state.get("retry_count", 0) + 1
    print(f"[agent] 重试第 {state['retry_count']} 次")

    messages = build_retry_messages(
        goal=state.get("goal", ""),
        user_message=state.get("user_message", ""),
        history=state.get("history", []),
        has_image=bool(state.get("img_b64")),
        image_size=state.get("img_size"),
        ocr_text=state.get("ocr_text", ""),
    )

    try:
        content = await call_model(
            messages["system"], messages["user"], state.get("img_b64"), temperature=0.0
        )
        parsed = safe_parse(content) or {}

        # 重试允许模型回答「找不到」
        if str(parsed.get("reply_type", "")).lower() == "text" and parsed.get("text_reply"):
            merged = dict(state.get("result") or {})
            merged.update({
                "reply_type": "text",
                "bbox": [0, 0, 0, 0],
                "bbox_valid": False,
                "text_reply": str(parsed["text_reply"]).strip(),
                "explanation": str(parsed.get("explanation") or "").strip(),
            })
            state["result"] = merged
            print("[agent] 重试结果：模型明确表示找不到，转文字回答")
            return state

        bbox, _ = normalize_bbox(parsed.get("bbox"), state.get("img_size"))
        if bbox:
            merged = dict(state.get("result") or {})
            for k in ("target", "action", "text_reply", "explanation", "confidence"):
                if parsed.get(k):
                    merged[k] = parsed[k]
            merged.update({"reply_type": "action", "bbox": bbox, "bbox_valid": True})
            state["result"] = merged
            print(f"[agent] 重试成功 {bbox}")
    except Exception as e:
        print(f"[agent] 重试失败：{e}")

    return state


# ============ 6. 收尾 ============
async def node_finalize(state: AgentState) -> AgentState:
    result = dict(state.get("result") or {})

    if result.get("reply_type") == "action" and not result.get("bbox_valid"):
        # 两次都没定位到，不要再给用户一个空框，改成文字说明
        reason = result.get("bbox_error") or "没有拿到有效坐标"
        text = result.get("text_reply") or (
            f"我在当前截图里没能确定「{state.get('goal') or '目标'}」对应的位置（{reason}）。"
            "可能这个入口在滚动条下面，或者藏在某个菜单里。"
            "你可以把要操作的那块区域截大一点，或者告诉我你是在哪个菜单下看到的，我再帮你定位。"
        )
        result.update({
            "reply_type": "text",
            "bbox": [0, 0, 0, 0],
            "bbox_valid": False,
            "text_reply": text,
        })

    if not result.get("text_reply") and not result.get("action"):
        if state.get("error"):
            result["text_reply"] = f"模型调用出错了：{state['error'][:120]}"
        else:
            result["text_reply"] = "我没能理解这一轮要做什么，可以说得再具体一点吗？"

    result.setdefault("target", "")
    result.setdefault("action", "")
    result.setdefault("explanation", "")
    result.setdefault("confidence", 0.0)
    state["result"] = result
    return state


def should_retry(state: AgentState) -> str:
    result = state.get("result", {}) or {}
    if result.get("reply_type") != "action":
        return "finalize"
    if result.get("bbox_valid"):
        return "finalize"
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "finalize"
    if not state.get("img_b64"):
        return "finalize"
    return "retry"


def build_agent():
    g = StateGraph(AgentState)

    g.add_node("check_task", node_check_task)
    g.add_node("gather_context", node_gather_context)
    g.add_node("call_model", node_call_model)
    g.add_node("validate", node_validate)
    g.add_node("retry", node_retry)
    g.add_node("finalize", node_finalize)

    g.set_entry_point("check_task")
    g.add_edge("check_task", "gather_context")
    g.add_edge("gather_context", "call_model")
    g.add_edge("call_model", "validate")
    g.add_conditional_edges("validate", should_retry, {"retry": "retry", "finalize": "finalize"})
    g.add_edge("retry", "validate")
    g.add_edge("finalize", END)

    return g.compile()


agent_graph = build_agent()
