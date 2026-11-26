import os
import io
import json
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

from alibabacloud_imagerecog20190930.client import Client as ImagerecogClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_imagerecog20190930 import models as imagerecog_models
from alibabacloud_tea_util import models as util_models

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

ALIBABA_CLOUD_ACCESS_KEY_ID = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

MAX_SIDE = 1280
MAX_BYTES = 3 * 1024 * 1024


def get_client():
    config = open_api_models.Config(
        access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET,
    )
    config.endpoint = "imagerecog.cn-shanghai.aliyuncs.com"
    return ImagerecogClient(config)


def detect_icons(img: Image.Image):
    """
    调用阿里云元素识别 API，检测图像中的元素。
    返回列表: [{"type": "text"/"person"/"decoration", "bbox": [x,y,w,h], "confidence": 0.9}]
    bbox 为归一化相对坐标 0-1。
    """
    if not ALIBABA_CLOUD_ACCESS_KEY_ID or not ALIBABA_CLOUD_ACCESS_KEY_SECRET:
        print("[icon] 阿里云 AccessKey 未配置，跳过图标检测")
        return []

    # 压缩到 API 限制内
    W, H = img.size
    if W > MAX_SIDE or H > MAX_SIDE:
        ratio = min(MAX_SIDE / W, MAX_SIDE / H)
        img = img.resize((int(W * ratio), int(H * ratio)), Image.LANCZOS)

    W2, H2 = img.size

    # 转字节
    buf = io.BytesIO()
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(buf, format="JPEG", quality=85)
    img_bytes = buf.getvalue()

    if len(img_bytes) > MAX_BYTES:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        img_bytes = buf.getvalue()
        if len(img_bytes) > MAX_BYTES:
            print(f"[icon] 图片过大 ({len(img_bytes)} bytes)，跳过")
            return []

    try:
        client = get_client()

        # 参数名是 url_object，需要传 BinaryIO
        request = imagerecog_models.DetectImageElementsAdvanceRequest(
            url_object=io.BytesIO(img_bytes),
        )
        runtime = util_models.RuntimeOptions()
        response = client.detect_image_elements_advance(request, runtime)

        result = response.body
        if not result or not result.data:
            print("[icon] 返回结果为空")
            return []

        # 解析 elements
        elements_raw = []
        data = result.data
        if hasattr(data, "elements") and data.elements:
            elements_raw = data.elements
        elif isinstance(data, dict):
            elements_raw = data.get("Elements", [])

        elements = []
        for item in elements_raw:
            bbox_px = None
            elem_type = "unknown"

            if hasattr(item, "rectangle") and item.rectangle:
                r = item.rectangle
                bbox_px = [r.left, r.top, r.right, r.bottom]
            elif isinstance(item, dict):
                rect = item.get("Rectangle") or {}
                if isinstance(rect, dict):
                    bbox_px = [rect.get("Left"), rect.get("Top"), rect.get("Right"), rect.get("Bottom")]

            if hasattr(item, "type"):
                elem_type = item.type
            elif isinstance(item, dict):
                elem_type = item.get("Type", "unknown")

            if not bbox_px or len(bbox_px) != 4 or None in bbox_px:
                continue

            x1, y1, x2, y2 = bbox_px
            bbox = [
                round(x1 / W2, 4),
                round(y1 / H2, 4),
                round((x2 - x1) / W2, 4),
                round((y2 - y1) / H2, 4),
            ]

            if bbox[2] <= 0.001 or bbox[3] <= 0.001:
                continue

            elements.append({
                "type": elem_type,
                "bbox": bbox,
                "confidence": 0.9,
            })

        print(f"[icon] 阿里云元素识别检测到 {len(elements)} 个元素")
        return elements

    except Exception as e:
        print(f"[icon] 阿里云元素识别调用失败: {e}")
        return []


def format_icon_candidates(elements, max_items=20):
    """把图标/元素清单格式化成给模型看的文本。"""
    if not elements:
        return "（未检测到图标元素）"

    elements = sorted(elements, key=lambda x: -x.get("confidence", 0))[:max_items]

    type_cn = {
        "person": "人物/物体",
        "decoration": "装饰元素",
        "text": "文案",
        "unknown": "未知",
    }

    lines = []
    for i, e in enumerate(elements, 1):
        x, y, w, h = e["bbox"]
        t = type_cn.get(e["type"], e["type"])
        lines.append(f'{i}. [{t}] 位置：[{x:.3f}, {y:.3f}, {w:.3f}, {h:.3f}]')
    return "\n".join(lines)