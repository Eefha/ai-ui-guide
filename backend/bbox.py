"""
bbox 归一化与校验。

模型给出的坐标经常是这几种情况之一，只有在入口处统一处理，前端才不会圈歪：
1. 相对坐标 [x, y, w, h]           —— 目标格式
2. 像素坐标 [47, 815, 90, 838]     —— 换个模型就会这样
3. 对角坐标 [x1, y1, x2, y2]       —— 溢出 1.0 时能识别出来
4. 点级别的小框（w=h=0.014）       —— 按中心点扩到可看见的尺寸
5. 全 0 / 负数 / 超出边界          —— 判为无效
"""
from typing import List, Optional, Sequence, Tuple

from config import MAX_BBOX_AREA, MIN_BBOX_SIDE

BBox = List[float]
Size = Tuple[int, int]


def _to_floats(raw) -> Optional[List[float]]:
    if raw is None or isinstance(raw, (str, bytes)):
        return None
    if not isinstance(raw, Sequence) or len(raw) != 4:
        return None
    try:
        return [float(v) for v in raw]
    except (TypeError, ValueError):
        return None


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def normalize_bbox(
    raw,
    size: Optional[Size] = None,
    min_side: float = MIN_BBOX_SIDE,
) -> Tuple[Optional[BBox], str]:
    """
    把模型吐出来的 bbox 归一化成 [x, y, w, h]（0~1）。
    合法则返回 (bbox, "")，不合法返回 (None, 原因)。
    size 为原图 (宽, 高)，仅在需要把像素坐标换算成相对坐标时使用。
    """
    vals = _to_floats(raw)
    if vals is None:
        return None, "bbox 不是 4 个数字"

    x, y, a, b = vals

    if x == 0 and y == 0 and a == 0 and b == 0:
        return None, "bbox 全为 0"

    if min(x, y, a, b) < 0:
        return None, "bbox 含负数"

    # 像素坐标 → 相对坐标
    if max(abs(x), abs(y), abs(a), abs(b)) > 1.2:
        if not size:
            return None, "疑似像素坐标，但拿不到图片尺寸"
        w_px, h_px = size
        if w_px <= 0 or h_px <= 0:
            return None, "图片尺寸异常"
        x, y, a, b = x / w_px, y / h_px, a / w_px, b / h_px

    # 对角坐标 → 宽高（仅在按 w/h 解释会溢出右边界时才这么判断）
    if (x + a > 1.02 or y + b > 1.02) and a > x and b > y:
        a, b = a - x, b - y
        if a <= 0 or b <= 0:
            return None, "bbox 换算后宽高为 0"

    w, h = a, b

    if w <= 0 or h <= 0:
        return None, "bbox 宽高必须为正数"

    # 越界裁剪
    if x > 1 or y > 1:
        return None, "bbox 起点超出图片范围"
    w = min(w, 1.0 - x)
    h = min(h, 1.0 - y)

    if w <= 0.001 or h <= 0.001:
        return None, "bbox 宽高过小"

    # 盖住小半屏，多半是把整块面板/整个窗口框进来了，不是可点的控件
    if w * h > MAX_BBOX_AREA:
        return None, f"bbox 面积过大（{w * h:.0%}），不像单个控件"

    # 点级别的小框 → 以中心点向外扩到可看见的尺寸
    if min_side > 0:
        if w < min_side:
            cx = x + w / 2
            w = min(min_side, 1.0)
            x = _clamp(cx - w / 2, 0.0, max(0.0, 1.0 - w))
        if h < min_side:
            cy = y + h / 2
            h = min(min_side, 1.0)
            y = _clamp(cy - h / 2, 0.0, max(0.0, 1.0 - h))

    return [round(x, 4), round(y, 4), round(w, 4), round(h, 4)], ""


def is_valid_bbox(raw, size: Optional[Size] = None) -> bool:
    return normalize_bbox(raw, size)[0] is not None


def bbox_center(bbox: BBox) -> Tuple[float, float]:
    x, y, w, h = bbox
    return round(x + w / 2, 4), round(y + h / 2, 4)


def same_bbox(a, b, tolerance: float = 0.012) -> bool:
    """两个框是否基本重合，用来避免同一动作被重复记进历史。"""
    if not a or not b or len(a) != 4 or len(b) != 4:
        return False
    return all(abs(float(ai) - float(bi)) <= tolerance for ai, bi in zip(a, b))
