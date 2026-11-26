import io
import json
from typing import List

from PIL import Image
from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_models
from alibabacloud_tea_util import models as util_models

import config


def get_ocr_client():
    cfg = open_api_models.Config(
        access_key_id=config.ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=config.ALIBABA_CLOUD_ACCESS_KEY_SECRET,
    )
    # 根据账号地域修改：杭州 cn-hangzhou / 北京 cn-beijing / 上海 cn-shanghai
    cfg.endpoint = config.OCR_ENDPOINT
    cfg.read_timeout = 15000
    cfg.connect_timeout = 5000
    return OcrClient(cfg)


def extract_text_elements(img: Image.Image):
    """
    调用阿里云 OCR 识别图片中的文字和位置。
    返回列表，每个元素包含 content 和 bbox（归一化坐标 0-1）。
    """
    client = get_ocr_client()
    W, H = img.size

    # 转字节流
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_bytes = buf.getvalue()

    request = ocr_models.RecognizeGeneralRequest(body=img_bytes)
    runtime = util_models.RuntimeOptions()

    try:
        response = client.recognize_general_with_options(request, runtime)
        result = response.body
        if not result or not result.data:
            return []

        # body.data 是 JSON 字符串
        data = json.loads(result.data)
        elements = []

        for word in data.get('prism_wordsInfo', []):
            text = word.get('word', '').strip()
            pos = word.get('pos', [])
            if not text or not pos:
                continue

            xs = [p['x'] for p in pos]
            ys = [p['y'] for p in pos]
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)

            # 归一化坐标
            bbox = [
                round(x1 / W, 4),
                round(y1 / H, 4),
                round((x2 - x1) / W, 4),
                round((y2 - y1) / H, 4),
            ]

            # 置信度：prob 是 0-100 的整数
            prob = word.get('prob', 100)
            confidence = round(prob / 100.0, 3)

            elements.append({
                "content": text,
                "bbox": bbox,
                "confidence": confidence,
            })

        return elements

    except Exception as e:
        print(f"[ocr] 阿里云 OCR 调用失败: {e}")
        raise


def format_candidates_for_prompt(elements, max_items: int = None) -> str:
    """
    把元素列表格式化成给模型看的候选清单。

    排序按「从上到下、从左到右」（按 y 分行、行内按 x），而不是按置信度：
    模型看界面是视野顺序的，按位置排它更容易读；按置信度排会把相邻的控件打散。
    """
    if not elements:
        return "（未检测到文字元素）"

    if max_items is None:
        max_items = config.OCR_MAX_ITEMS

    elements = [e for e in elements if e["confidence"] >= config.OCR_MIN_CONFIDENCE]
    if not elements:
        return "（未检测到可用文字元素）"

    # 先按 y 聚类成"行"（同一行内 y 差小于 1.5% 视为同一行），行内再按 x 排
    elements.sort(key=lambda e: (e["bbox"][1], e["bbox"][0]))
    rows: List[List[dict]] = []
    for e in elements:
        if rows and abs(e["bbox"][1] - rows[-1][0]["bbox"][1]) < 0.015:
            rows[-1].append(e)
        else:
            rows.append([e])

    ordered: List[dict] = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda e: e["bbox"][0]))
    ordered = ordered[:max_items]

    lines = []
    for i, e in enumerate(ordered, 1):
        x, y, w, h = e["bbox"]
        lines.append(
            f'{i}. 文字："{e["content"]}"  位置：[{x:.3f}, {y:.3f}, {w:.3f}, {h:.3f}]'
        )
    return "\n".join(lines)