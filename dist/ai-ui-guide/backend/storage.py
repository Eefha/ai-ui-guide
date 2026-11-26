import sqlite3
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
IMAGES_DIR = DATA_DIR / "sessions_files"
DB_PATH = DATA_DIR / "app.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_conn()
    try:
        # 用户表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        # 验证码表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                email TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        # 会话表（加 user_id）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT NOT NULL DEFAULT '新对话',
                goal TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")

        # messages 表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT DEFAULT '',
                image_url TEXT DEFAULT '',
                reply_type TEXT DEFAULT '',
                target TEXT DEFAULT '',
                bbox TEXT DEFAULT '',
                bbox_valid INTEGER DEFAULT 0,
                action TEXT DEFAULT '',
                text_reply TEXT DEFAULT '',
                explanation TEXT DEFAULT '',
                confidence REAL DEFAULT 0,
                is_new_task INTEGER DEFAULT 0,
                mode TEXT DEFAULT '',
                ocr_debug TEXT DEFAULT '',
                icon_debug TEXT DEFAULT '',
                rag_debug TEXT DEFAULT '',
                web_debug TEXT DEFAULT '',
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                step_index INTEGER NOT NULL,
                action TEXT DEFAULT '',
                bbox TEXT DEFAULT '',
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_history_session ON history(session_id)")

        conn.commit()

        # 兼容旧表
        for col in ["ocr_debug", "icon_debug", "rag_debug", "web_debug"]:
            try:
                conn.execute(f"ALTER TABLE messages ADD COLUMN {col} TEXT DEFAULT ''")
                conn.commit()
            except sqlite3.OperationalError:
                pass
        try:
            conn.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
    finally:
        conn.close()


init_db()


# ============ 用户 ============
def get_or_create_user(email: str) -> dict:
    """根据邮箱查找或创建用户"""
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return {"id": row["id"], "email": row["email"]}
        uid = uuid.uuid4().hex[:16]
        conn.execute(
            "INSERT INTO users (id, email, created_at) VALUES (?, ?, ?)",
            (uid, email, now_iso()),
        )
        conn.commit()
        return {"id": uid, "email": email}
    finally:
        conn.close()


# ============ 验证码 ============
def save_verification_code(email: str, code: str, expires_at: str):
    conn = get_conn()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO verification_codes (email, code, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        """, (email, code, expires_at, now_iso()))
        conn.commit()
    finally:
        conn.close()


def get_verification_code(email: str) -> Optional[dict]:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM verification_codes WHERE email = ?", (email,)
        ).fetchone()
        if not row:
            return None
        return {
            "code": row["code"],
            "expires_at": row["expires_at"],
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def delete_verification_code(email: str):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
        conn.commit()
    finally:
        conn.close()


# ============ 会话 ============
def new_session(user_id: str, title: str = "新对话") -> dict:
    sid = uuid.uuid4().hex[:12]
    now = now_iso()
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO sessions (id, user_id, title, goal, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (sid, user_id, title, "", now, now),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "id": sid, "user_id": user_id, "title": title, "goal": "",
        "history": [], "messages": [],
        "created_at": now, "updated_at": now,
    }


def get_session(sid: str, user_id: Optional[str] = None) -> Optional[dict]:
    conn = get_conn()
    try:
        if user_id:
            row = conn.execute(
                "SELECT * FROM sessions WHERE id = ? AND user_id = ?", (sid, user_id)
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        if not row:
            return None

        session = {
            "id": row["id"],
            "user_id": row["user_id"] if "user_id" in row.keys() else None,
            "title": row["title"],
            "goal": row["goal"] or "",
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "messages": [],
            "history": [],
        }

        mrows = conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (sid,)
        ).fetchall()
        for m in mrows:
            try:
                bbox = json.loads(m["bbox"]) if m["bbox"] else [0, 0, 0, 0]
            except Exception:
                bbox = [0, 0, 0, 0]
            msg = {
                "role": m["role"],
                "text": m["text"],
                "image_url": m["image_url"],
                "reply_type": m["reply_type"],
                "target": m["target"],
                "bbox": bbox,
                "bbox_valid": bool(m["bbox_valid"]),
                "action": m["action"],
                "text_reply": m["text_reply"],
                "explanation": m["explanation"],
                "confidence": m["confidence"],
                "is_new_task": bool(m["is_new_task"]),
                "mode": m["mode"],
                "timestamp": m["timestamp"],
            }
            for col in ["ocr_debug", "icon_debug", "rag_debug", "web_debug"]:
                try:
                    msg[col] = _safe_json(m[col])
                except Exception:
                    msg[col] = None
            session["messages"].append(msg)

        hrows = conn.execute(
            "SELECT * FROM history WHERE session_id = ? ORDER BY step_index ASC", (sid,)
        ).fetchall()
        for h in hrows:
            try:
                bbox = json.loads(h["bbox"]) if h["bbox"] else [0, 0, 0, 0]
            except Exception:
                bbox = [0, 0, 0, 0]
            session["history"].append({"action": h["action"], "bbox": bbox})

        return session
    finally:
        conn.close()


def list_sessions(user_id: str) -> List[dict]:
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT s.id, s.title, s.updated_at,
                   (SELECT COUNT(*) FROM messages WHERE session_id = s.id) AS msg_count
            FROM sessions s
            WHERE s.user_id = ?
            ORDER BY s.updated_at DESC
        """, (user_id,)).fetchall()
        return [{
            "id": r["id"],
            "title": r["title"],
            "updated_at": r["updated_at"],
            "message_count": r["msg_count"],
        } for r in rows]
    finally:
        conn.close()


def delete_session(sid: str, user_id: str) -> bool:
    conn = get_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE id = ? AND user_id = ?", (sid, user_id))
        conn.commit()
    finally:
        conn.close()
    img_dir = IMAGES_DIR / sid
    if img_dir.exists():
        shutil.rmtree(img_dir)
    return True


def save_image(sid: str, file_bytes: bytes, ext: str = "png") -> str:
    img_dir = IMAGES_DIR / sid
    img_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:10]}.{ext}"
    (img_dir / filename).write_bytes(file_bytes)
    return f"/sessions_files/{sid}/{filename}"


def add_message(sid: str, message: dict):
    conn = get_conn()
    try:
        bbox = message.get("bbox") or [0, 0, 0, 0]
        ocr_debug = message.get("ocr_debug")
        icon_debug = message.get("icon_debug")
        rag_debug = message.get("rag_debug")
        web_debug = message.get("web_debug")
        conn.execute("""
            INSERT INTO messages
            (session_id, role, text, image_url, reply_type, target, bbox, bbox_valid,
             action, text_reply, explanation, confidence, is_new_task, mode,
             ocr_debug, icon_debug, rag_debug, web_debug, timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            sid,
            message.get("role", ""),
            message.get("text", ""),
            message.get("image_url", ""),
            message.get("reply_type", ""),
            message.get("target", ""),
            json.dumps(bbox),
            1 if message.get("bbox_valid") else 0,
            message.get("action", ""),
            message.get("text_reply", ""),
            message.get("explanation", ""),
            float(message.get("confidence", 0) or 0),
            1 if message.get("is_new_task") else 0,
            message.get("mode", ""),
            json.dumps(ocr_debug) if ocr_debug else "",
            json.dumps(icon_debug) if icon_debug else "",
            json.dumps(rag_debug) if rag_debug else "",
            json.dumps(web_debug) if web_debug else "",
            message.get("timestamp", now_iso()),
        ))
        conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now_iso(), sid))
        conn.commit()
    finally:
        conn.close()


def delete_last_message(sid: str, role: Optional[str] = None) -> bool:
    """删掉最后一条消息（role 可限定），用于「重新生成」替换上一条回答。"""
    conn = get_conn()
    try:
        if role:
            row = conn.execute(
                "SELECT id FROM messages WHERE session_id = ? AND role = ? ORDER BY id DESC LIMIT 1",
                (sid, role),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                (sid,),
            ).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM messages WHERE id = ?", (row["id"],))
        conn.commit()
        return True
    finally:
        conn.close()


def update_session(sid: str, **fields):
    conn = get_conn()
    try:
        if "history" in fields:
            history = fields.pop("history")
            conn.execute("DELETE FROM history WHERE session_id = ?", (sid,))
            for i, h in enumerate(history):
                conn.execute(
                    "INSERT INTO history (session_id, step_index, action, bbox) VALUES (?,?,?,?)",
                    (sid, i, h.get("action", ""), json.dumps(h.get("bbox") or [0, 0, 0, 0])),
                )

        if "goal" in fields:
            conn.execute("UPDATE sessions SET goal = ? WHERE id = ?", (fields.pop("goal"), sid))
        if "title" in fields:
            conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (fields.pop("title"), sid))

        conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now_iso(), sid))
        conn.commit()
    finally:
        conn.close()


def auto_title(sid: str, text: str):
    conn = get_conn()
    try:
        row = conn.execute("SELECT title FROM sessions WHERE id = ?", (sid,)).fetchone()
        if not row:
            return
        if row["title"] in ("新对话", "", None) and text:
            title = text.strip().replace("\n", " ")[:20]
            if title:
                conn.execute(
                    "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                    (title, now_iso(), sid),
                )
                conn.commit()
    finally:
        conn.close()


# ============ 游客数据同步 ============
def transfer_sessions(from_user_id: str, to_user_id: str) -> int:
    """把 from_user_id 的所有 sessions 迁移到 to_user_id，返回迁移数量"""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id FROM sessions WHERE user_id = ?", (from_user_id,)
        ).fetchall()
        count = len(rows)
        if count > 0:
            conn.execute(
                "UPDATE sessions SET user_id = ?, updated_at = ? WHERE user_id = ?",
                (to_user_id, now_iso(), from_user_id),
            )
            conn.commit()
        return count
    finally:
        conn.close()


def _safe_json(s):
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None