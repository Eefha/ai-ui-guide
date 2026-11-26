"""
全局配置：环境变量、模型、阈值、路径的唯一来源。
其它模块一律从这里取值，不要再各自 load_dotenv。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH, override=True)


def _str(key: str, default: str = "") -> str:
    v = os.environ.get(key)
    return v.strip() if isinstance(v, str) and v.strip() else default


def _int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, ""))
    except (TypeError, ValueError):
        return default


def _float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, ""))
    except (TypeError, ValueError):
        return default


def _bool(key: str, default: bool) -> bool:
    v = os.environ.get(key)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


# ============ 路径 ============
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATA_DIR = BASE_DIR / "data"

# ============ 模型 ============
DASHSCOPE_API_KEY = _str("DASHSCOPE_API_KEY")
# 主模型：需要同时具备视觉理解 + JSON 输出能力。
# 实测同样一张 1919×1079 的 IDE 截图、同样的问题：
#   qwen3-vl-plus        5~8s    定位准确
#   qwen3.8-omni-flash   27~83s  同样准确，但慢一个数量级（omni 主打音视频，不适合纯截图任务）
# 想换回去在 .env 里设置 QWEN_MODEL 即可。
MODEL_NAME = _str("QWEN_MODEL", "qwen3-vl-plus")
# 建索引时给图片写描述用的模型，默认与主模型一致
VLM_MODEL = _str("QWEN_VLM_MODEL", MODEL_NAME)
API_URL = _str("QWEN_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")

LLM_TIMEOUT = _float("LLM_TIMEOUT", 60.0)
LLM_TEMPERATURE = _float("LLM_TEMPERATURE", 0.1)
LLM_MAX_ATTEMPTS = _int("LLM_MAX_ATTEMPTS", 2)

# ============ 图片预处理 ============
# 送模型前把长边压到这个尺寸以内：坐标基于压缩后的图算，但比例不变，仍可直接用
IMAGE_MAX_SIDE = _int("IMAGE_MAX_SIDE", 1600)
IMAGE_JPEG_QUALITY = _int("IMAGE_JPEG_QUALITY", 85)

# ============ 会话上下文 ============
# 送进提示词的「已完成步骤」上限
MAX_HISTORY_STEPS = _int("MAX_HISTORY_STEPS", 5)
# 新任务判定：与旧目标的语义相似度低于该值即认为换任务
SIMILARITY_THRESHOLD = _float("SIMILARITY_THRESHOLD", 0.55)

# ============ RAG ============
RAG_TOP_K = _int("RAG_TOP_K", 3)
# 余弦相似度下限。实测：真正相关的片段在 0.75~0.85，沾边的 0.6 左右，无关的 0.5 上下。
# 旧值 0.8 会把所有内容都挡在外面，导致每次都去联网。
RAG_MIN_SCORE = _float("RAG_MIN_SCORE", 0.65)
ENABLE_RAG = _bool("ENABLE_RAG", True)

# ============ 联网搜索 ============
ENABLE_WEB_SEARCH = _bool("ENABLE_WEB_SEARCH", True)
# 带截图时默认不联网：用户问的是"这个界面上点哪"，网上搜不到答案，
# 只会白等几秒并把无关内容塞进提示词。纯文字提问时才联网。
WEB_SEARCH_WITH_IMAGE = _bool("WEB_SEARCH_WITH_IMAGE", False)
WEB_TOP_K = _int("WEB_TOP_K", 6)
WEB_MIN_SCORE = _float("WEB_MIN_SCORE", 0.55)
BAIDU_SEARCH_API_KEY = _str("BAIDU_SEARCH_API_KEY")

# ============ OCR ============
ENABLE_OCR = _bool("ENABLE_OCR", True)
OCR_MAX_ITEMS = _int("OCR_MAX_ITEMS", 40)
OCR_MIN_CONFIDENCE = _float("OCR_MIN_CONFIDENCE", 0.5)
OCR_ENDPOINT = _str("OCR_ENDPOINT", "ocr-api.cn-hangzhou.aliyuncs.com")
ALIBABA_CLOUD_ACCESS_KEY_ID = _str("ALIBABA_CLOUD_ACCESS_KEY_ID")
ALIBABA_CLOUD_ACCESS_KEY_SECRET = _str("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

# ============ bbox 后处理 ============
# 模型经常给出「点」级别的小框，按中心点扩到这个最小尺寸，否则前端几乎看不见
MIN_BBOX_SIDE = _float("MIN_BBOX_SIDE", 0.028)
# 单个控件不该占掉小半屏。超过这个面积比例，多半是把整块面板框进来了
MAX_BBOX_AREA = _float("MAX_BBOX_AREA", 0.45)

# ============ 认证 ============
JWT_SECRET = _str("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = _int("JWT_EXPIRE_DAYS", 7)
CODE_EXPIRE_MINUTES = _int("CODE_EXPIRE_MINUTES", 10)
CODE_LENGTH = 6

# ============ 邮件 ============
SMTP_HOST = _str("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = _int("SMTP_PORT", 587)
SMTP_USER = _str("SMTP_USER")
SMTP_PASSWORD = _str("SMTP_PASSWORD")
SMTP_FROM_NAME = _str("SMTP_FROM_NAME", "AI 软件操作引导")
