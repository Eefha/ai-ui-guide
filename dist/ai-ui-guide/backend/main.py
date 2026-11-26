import io
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

import config
import storage
from agent_graph import agent_graph
from auth import (
    CODE_EXPIRE_MINUTES,
    create_jwt,
    generate_code,
    get_current_user,
    is_guest,
    send_verification_email,
)
from bbox import normalize_bbox, same_bbox
from llm_utils import prepare_image
from rag import IMAGES_DIR as RAG_IMAGES_DIR

FRONTEND_DIR = config.FRONTEND_DIR

app = FastAPI(title="AI 软件操作引导")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/sessions_files", StaticFiles(directory=str(storage.IMAGES_DIR)), name="sessions_files")
app.mount("/rag_images", StaticFiles(directory=str(RAG_IMAGES_DIR)), name="rag_images")


@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "api_key_set": bool(config.DASHSCOPE_API_KEY),
        "model": config.MODEL_NAME,
        "rag": config.ENABLE_RAG,
        "web_search": config.ENABLE_WEB_SEARCH,
        "ocr": config.ENABLE_OCR,
    }


# ============ 认证接口 ============
@app.post("/auth/send_code")
async def send_code(email: str = Form(...)):
    email = email.strip().lower()
    if "@" not in email or len(email) < 5:
        raise HTTPException(400, "邮箱格式不正确")

    # 简单频率限制：同一邮箱 60 秒内只能发一次
    existing = storage.get_verification_code(email)
    if existing and existing.get("created_at"):
        try:
            elapsed = (datetime.now() - datetime.fromisoformat(existing["created_at"])).total_seconds()
            if elapsed < 60:
                raise HTTPException(429, f"发送太频繁，请 {int(60 - elapsed)} 秒后再试")
        except ValueError:
            pass

    code = generate_code()
    expires_at = (datetime.now() + timedelta(minutes=CODE_EXPIRE_MINUTES)).isoformat(timespec="seconds")

    storage.save_verification_code(email, code, expires_at)

    try:
        await send_verification_email(email, code)
    except Exception as e:
        print(f"[auth] 发送邮件失败：{e}")
        raise HTTPException(500, f"发送邮件失败：{str(e)[:100]}")

    return {"status": "ok", "message": f"验证码已发送到 {email}"}


@app.post("/auth/verify")
async def verify_code(email: str = Form(...), code: str = Form(...)):
    email = email.strip().lower()
    code = code.strip()

    record = storage.get_verification_code(email)
    if not record:
        raise HTTPException(400, "验证码不存在或已过期")

    if datetime.fromisoformat(record["expires_at"]) < datetime.now():
        storage.delete_verification_code(email)
        raise HTTPException(400, "验证码已过期")

    if record["code"] != code:
        raise HTTPException(400, "验证码不正确")

    user = storage.get_or_create_user(email)
    storage.delete_verification_code(email)

    token = create_jwt(user["id"], user["email"])
    return {
        "status": "ok",
        "token": token,
        "user": {"id": user["id"], "email": user["email"]},
    }


@app.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    if is_guest(user_id):
        return {"is_guest": True, "user_id": user_id}
    conn = storage.get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(401, "用户不存在")
        return {"is_guest": False, "user": {"id": row["id"], "email": row["email"]}}
    finally:
        conn.close()


@app.post("/auth/sync")
async def sync_guest_data(guest_id: str = Form(...), user_id: str = Depends(get_current_user)):
    if is_guest(user_id):
        raise HTTPException(400, "当前是游客身份，无法同步")
    if not guest_id.startswith("guest_"):
        raise HTTPException(400, "guest_id 格式错误")

    count = storage.transfer_sessions(guest_id, user_id)
    print(f"[auth] 游客 {guest_id} 的 {count} 个会话已迁移到用户 {user_id}")
    return {"status": "ok", "transferred": count}


# ============ 会话接口 ============
@app.get("/sessions")
def list_sessions_api(user_id: str = Depends(get_current_user)):
    return {"sessions": storage.list_sessions(user_id)}


@app.post("/sessions")
def create_session(user_id: str = Depends(get_current_user)):
    return {"session": storage.new_session(user_id)}


@app.get("/sessions/{sid}")
def get_session_api(sid: str, user_id: str = Depends(get_current_user)):
    s = storage.get_session(sid, user_id)
    if not s:
        raise HTTPException(status_code=404, detail="session not found")
    return {"session": s}


@app.delete("/sessions/{sid}")
def delete_session_api(sid: str, user_id: str = Depends(get_current_user)):
    storage.delete_session(sid, user_id)
    return {"ok": True}


# ============ 分析接口 ============
def _image_ext(raw: bytes) -> str:
    if raw[:3] == b"\xff\xd8\xff":
        return "jpg"
    if raw[:8].startswith(b"\x89PNG"):
        return "png"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    return "png"


def _load_image_from_url(url: str):
    """从会话目录里读回之前上传的图，返回 (bytes, PIL.Image) 或 (None, None)。"""
    if not url:
        return None, None
    disk_path = storage.IMAGES_DIR / url.replace("/sessions_files/", "")
    if not disk_path.exists():
        return None, None
    raw = disk_path.read_bytes()
    try:
        return raw, Image.open(io.BytesIO(raw))
    except Exception as e:
        print(f"[analyze] 读取历史图片失败：{e}")
        return None, None


def _last_user_image_url(session: dict) -> str:
    for m in reversed(session.get("messages", [])):
        if m.get("role") == "user" and m.get("image_url"):
            return m["image_url"]
    return ""


@app.post("/analyze")
async def analyze(
    user_id: str = Depends(get_current_user),
    image: UploadFile = File(None),
    session_id: str = Form(""),
    user_message: str = Form(""),
    mode: str = Form(""),          # 保留字段，实际模式由后端按「有无图/有无文字」判定
    force_new_task: str = Form("false"),
    regenerate: str = Form("false"),
):
    if not config.DASHSCOPE_API_KEY:
        return _err("未配置 API Key", "请在 backend/.env 中配置 DASHSCOPE_API_KEY")

    is_regenerate = str(regenerate).lower() == "true"
    force_new = str(force_new_task).lower() == "true"

    session = storage.get_session(session_id, user_id) if session_id else None
    if not session:
        session = storage.new_session(user_id)
        if session_id:
            print(f"[session] 找不到会话 {session_id}，已新建 {session['id']}")

    sid = session["id"]
    goal = session.get("goal", "")
    history_list = session.get("history", [])
    messages = session.get("messages", [])

    user_message = (user_message or "").strip()

    # ---------- 准备这一轮的输入 ----------
    img_b64 = None
    img_size = None
    img_bytes = None
    user_image_url = ""
    image_is_fresh = False

    if is_regenerate:
        last_user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        if not last_user_msg:
            return _err("无法重新生成", "找不到上一次的用户消息")

        user_message = (last_user_msg.get("text") or "").strip()
        img_bytes, img = _load_image_from_url(last_user_msg.get("image_url", ""))
        if img is not None:
            img_b64, img_size = prepare_image(img)
            user_image_url = last_user_msg.get("image_url", "")
            image_is_fresh = True

        # 重新生成 = 替换上一条回答，而不是再加一条。
        # 如果上一条回答记了一步进度，也要退掉，否则模型会以为这一步已经做过了。
        last_ai = messages[-1] if messages and messages[-1].get("role") == "ai" else None
        if last_ai and last_ai.get("reply_type") == "action" and last_ai.get("bbox_valid") and history_list:
            history_list = history_list[:-1]
            storage.update_session(sid, history=history_list)
        storage.delete_last_message(sid, role="ai")

    else:
        has_new_image = image is not None
        if not has_new_image and not user_message:
            return _err("无内容", "没有图片也没有文字")

        if has_new_image:
            img_bytes = await image.read()
            if not img_bytes:
                return _err("图片为空", "上传的图片读不到内容")
            user_image_url = storage.save_image(sid, img_bytes, _image_ext(img_bytes))
            try:
                img = Image.open(io.BytesIO(img_bytes))
                img.load()
            except Exception as e:
                return _err("图片无法解析", f"看起来不是有效的图片文件：{e}", user_image_url)
            img_b64, img_size = prepare_image(img)
            image_is_fresh = True
        else:
            # 没发新图，但会话里有过图：继续在同一张图上引导
            last_url = _last_user_image_url(session)
            img_bytes, img = _load_image_from_url(last_url)
            if img is not None:
                img_b64, img_size = prepare_image(img)
                user_image_url = last_url
                image_is_fresh = False

    has_image = img_b64 is not None
    has_text = bool(user_message)

    if has_image and has_text:
        effective_mode = "step"
    elif has_image:
        effective_mode = "ask"
    else:
        effective_mode = "text"

    # ---------- 落库用户消息 ----------
    if not is_regenerate:
        storage.add_message(sid, {
            "role": "user",
            "text": user_message,
            "image_url": user_image_url,
            "timestamp": storage.now_iso(),
            "mode": effective_mode,
        })
        if user_message:
            storage.auto_title(sid, user_message)
            if not goal:
                goal = user_message
                storage.update_session(sid, goal=goal)

    initial_state = {
        "session_id": sid,
        "user_message": user_message,
        "img_b64": img_b64,
        "img_size": img_size,
        "img_bytes": img_bytes,
        "mode": effective_mode,
        "force_new": force_new,
        "image_is_fresh": image_is_fresh,
        "goal": goal,
        "history": history_list,
        "is_new_task": False,
        "new_task_reason": None,
        "ocr_text": "",
        "ocr_debug": {"enabled": False, "count": 0, "samples": [], "elements": [], "error": ""},
        "rag_text": "",
        "rag_debug": {"enabled": False, "count": 0, "samples": [], "error": ""},
        "rag_hit": False,
        "web_text": "",
        "web_debug": {"enabled": False, "count": 0, "samples": [], "error": ""},
        "result": {},
        "retry_count": 0,
        "error": "",
    }

    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        print(f"[analyze] agent 执行失败：{e}")
        return _err("Agent 执行失败", str(e)[:300], user_image_url)

    result = dict(final_state.get("result") or {})
    ocr_debug = final_state.get("ocr_debug") or {}
    rag_debug = final_state.get("rag_debug") or {}
    web_debug = final_state.get("web_debug") or {}
    is_new_task = bool(final_state.get("is_new_task"))

    # ---------- 兜底校验（agent 已做过一次，这里保证出口一定合法） ----------
    reply_type = result.get("reply_type") if result.get("reply_type") in ("action", "text") else "text"
    if not has_image:
        reply_type = "text"

    bbox, bbox_error = ([0, 0, 0, 0], "")
    if reply_type == "action":
        bbox, bbox_error = normalize_bbox(result.get("bbox"), img_size)
        if bbox is None:
            reply_type = "text"
            bbox = [0, 0, 0, 0]

    payload = {
        "reply_type": reply_type,
        "target": (result.get("target") or "") if reply_type == "action" else "",
        "bbox": bbox,
        "bbox_valid": reply_type == "action" and bbox_error == "",
        "action": (result.get("action") or "") if reply_type == "action" else "",
        "text_reply": (result.get("text_reply") or "").strip(),
        "explanation": (result.get("explanation") or "").strip(),
        "confidence": result.get("confidence", 0.0),
        "is_new_task": is_new_task,
        "new_task_reason": final_state.get("new_task_reason"),
    }

    if payload["reply_type"] == "text" and not payload["text_reply"]:
        payload["text_reply"] = payload["explanation"] or "我暂时没能确定下一步该点哪里，可以说得再具体一点吗？"

    # ---------- 新任务：重置目标与进度 ----------
    if is_new_task:
        goal = user_message or ""
        history_list = []
        storage.update_session(sid, goal=goal, history=history_list)

    # ---------- 落库 AI 消息 ----------
    storage.add_message(sid, {
        "role": "ai",
        **payload,
        "mode": effective_mode,
        "image_url": user_image_url,
        "timestamp": storage.now_iso(),
        "ocr_debug": ocr_debug,
        "icon_debug": {"enabled": False, "count": 0, "samples": [], "elements": []},
        "rag_debug": rag_debug,
        "web_debug": web_debug,
    })

    # ---------- 更新进度（只在真的给出可点击位置时记一步，且不重复记同一步） ----------
    if payload["reply_type"] == "action" and payload["bbox_valid"]:
        step = {"action": payload["action"], "target": payload["target"], "bbox": payload["bbox"]}
        prev = history_list[-1] if history_list else None
        if not prev or not _same_step(prev, step):
            storage.update_session(sid, history=history_list + [step])

    return {
        "session_id": sid,
        "user_image_url": user_image_url,
        "effective_mode": effective_mode,
        "is_regenerate": is_regenerate,
        "template": final_state.get("template", ""),
        "ocr_debug": ocr_debug,
        "icon_debug": {"enabled": False, "count": 0, "samples": [], "elements": []},
        "rag_debug": rag_debug,
        "web_debug": web_debug,
        **payload,
    }


def _same_step(a: dict, b: dict) -> bool:
    """动作描述和坐标都一样，就认为是同一步（target 存在历史表里会被丢，不参与比较）。"""
    return a.get("action") == b.get("action") and same_bbox(a.get("bbox"), b.get("bbox"))


def _err(action, explanation, user_image_url=""):
    return {
        "target": "错误",
        "bbox": [0, 0, 0, 0],
        "action": action,
        "text_reply": "",
        "explanation": explanation,
        "confidence": 0.0,
        "bbox_valid": False,
        "is_new_task": False,
        "reply_type": "text",
        "effective_mode": "text",
        "user_image_url": user_image_url,
        "ocr_debug": {"enabled": False, "count": 0, "samples": [], "elements": [], "error": ""},
        "icon_debug": {"enabled": False, "count": 0, "samples": [], "elements": [], "error": ""},
        "rag_debug": {"enabled": False, "count": 0, "samples": [], "error": ""},
        "web_debug": {"enabled": False, "count": 0, "samples": [], "error": ""},
    }
