"""
认证模块：邮箱验证码 + JWT + 游客身份
支持 587 STARTTLS 和 465 SSL 双通道，自动降级
兼容 Python 3.11 / 3.12 / 3.14
"""
import asyncio
import random
import smtplib
import ssl
import string
from datetime import datetime, timedelta
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from typing import Optional

import jwt
from fastapi import HTTPException, Header as FastAPIHeader

import config

# ============ JWT 配置 ============
JWT_SECRET = config.JWT_SECRET
JWT_ALGORITHM = config.JWT_ALGORITHM
JWT_EXPIRE_DAYS = config.JWT_EXPIRE_DAYS

# ============ SMTP 配置 ============
SMTP_HOST = config.SMTP_HOST
SMTP_PORT = config.SMTP_PORT
SMTP_USER = config.SMTP_USER
SMTP_PASSWORD = config.SMTP_PASSWORD
SMTP_FROM_NAME = config.SMTP_FROM_NAME

# ============ 验证码配置 ============
CODE_EXPIRE_MINUTES = config.CODE_EXPIRE_MINUTES
CODE_LENGTH = config.CODE_LENGTH


def generate_code() -> str:
    """生成 6 位数字验证码"""
    return "".join(random.choices(string.digits, k=CODE_LENGTH))


def create_jwt(user_id: str, email: str) -> str:
    """签发 JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> Optional[dict]:
    """验证 JWT，返回 payload 或 None"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def _encode_header(value: str) -> str:
    """
    兼容 Python 3.11 / 3.12 / 3.14 的 Header 编码
    - 3.14 之前：Header(value, 'utf-8')
    - 3.14+ ：Header(value, charset='utf-8')
    """
    try:
        # 优先尝试新写法（关键字参数）
        return str(Header(value, charset="utf-8"))
    except TypeError:
        # 降级到旧写法（位置参数）
        return str(Header(value, "utf-8"))


def _build_message(to_email: str, code: str) -> MIMEMultipart:
    """构造邮件对象"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = _encode_header(f"【{SMTP_FROM_NAME}】登录验证码")
    msg["From"] = formataddr((_encode_header(SMTP_FROM_NAME), SMTP_USER))
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()

    html = f"""
    <html>
    <body style="font-family: sans-serif; padding: 20px;">
        <h2>登录验证码</h2>
        <p>您的验证码是：</p>
        <h1 style="color: #4f6ef7; font-size: 32px; letter-spacing: 6px;">{code}</h1>
        <p style="color: #6b7280;">验证码 {CODE_EXPIRE_MINUTES} 分钟内有效，请勿泄露给他人。</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
        <p style="color: #9ca3af; font-size: 12px;">如果这不是您的操作，请忽略此邮件。</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def _send_via_starttls(msg: MIMEMultipart, to_email: str):
    """方式 1：587 STARTTLS"""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    with smtplib.SMTP(SMTP_HOST, 587, timeout=20) as server:
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())


def _send_via_ssl(msg: MIMEMultipart, to_email: str):
    """方式 2：465 SSL"""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    with smtplib.SMTP_SSL(SMTP_HOST, 465, timeout=20, context=ctx) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())


def _send_email_sync(to_email: str, code: str):
    """
    同步发送邮件
    先尝试 587 STARTTLS，失败再尝试 465 SSL
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP 未配置，请检查 .env 中的 SMTP_USER 和 SMTP_PASSWORD")

    msg = _build_message(to_email, code)

    # 方式 1：587 STARTTLS
    try:
        print(f"[SMTP] 尝试 {SMTP_HOST}:587 + STARTTLS ...")
        _send_via_starttls(msg, to_email)
        print(f"[SMTP] ✅ 587 发送成功")
        return
    except Exception as e:
        print(f"[SMTP] ❌ 587 失败：{type(e).__name__}: {e}")

    # 方式 2：465 SSL
    try:
        print(f"[SMTP] 尝试 {SMTP_HOST}:465 + SSL ...")
        _send_via_ssl(msg, to_email)
        print(f"[SMTP] ✅ 465 发送成功")
        return
    except Exception as e:
        print(f"[SMTP] ❌ 465 失败：{type(e).__name__}: {e}")

    raise RuntimeError("587 和 465 都发送失败，请查看终端日志")


async def send_verification_email(to_email: str, code: str):
    """异步发送邮件（用 to_thread 包装同步调用）"""
    await asyncio.to_thread(_send_email_sync, to_email, code)


# ============ FastAPI 依赖：身份识别 ============
async def get_current_user(
    authorization: Optional[str] = FastAPIHeader(None),
    x_guest_id: Optional[str] = FastAPIHeader(None),
) -> str:
    """
    识别当前请求的用户身份：
    1. 优先用 JWT token（已登录）
    2. 其次用 guest_id（游客模式）

    返回 user_id（真实用户）或 guest_id（游客）
    """
    # 1. 尝试 JWT
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = verify_jwt(token)
        if payload:
            return payload["user_id"]
        raise HTTPException(status_code=401, detail="Token 无效或已过期")

    # 2. 尝试 guest_id
    if x_guest_id and x_guest_id.startswith("guest_"):
        return x_guest_id

    raise HTTPException(status_code=401, detail="未提供身份标识")


def is_guest(user_id: str) -> bool:
    """判断是否是游客"""
    return user_id.startswith("guest_")