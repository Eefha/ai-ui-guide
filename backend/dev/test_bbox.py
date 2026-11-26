"""
bbox 归一化单元测试（不依赖网络）。

    .venv\\Scripts\\python.exe dev\\test_bbox.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bbox import normalize_bbox, same_bbox  # noqa: E402

CASES = [
    # (说明, 输入, 图片尺寸, 期望通过)
    ("标准相对坐标", [0.5, 0.5, 0.1, 0.05], (1920, 1080), True),
    ("像素坐标", [960, 540, 192, 54], (1920, 1080), True),
    ("像素对角坐标", [960, 540, 1152, 594], (1920, 1080), True),
    ("点级别小框", [0.5, 0.5, 0.008, 0.008], (1920, 1080), True),
    ("全 0", [0, 0, 0, 0], (1920, 1080), False),
    ("负数", [-1, 0.2, 0.1, 0.1], (1920, 1080), False),
    ("宽为 0", [0.2, 0.2, 0, 0.1], (1920, 1080), False),
    ("只有 3 个数", [0.1, 0.2, 0.3], (1920, 1080), False),
    ("字符串", "0.1,0.2,0.3,0.4", (1920, 1080), False),
    ("几乎整屏", [0.01, 0.01, 0.99, 0.99], (1920, 1080), False),
    ("框住半个面板", [0.05, 0.10, 0.60, 0.80], (1920, 1080), False),
    ("大按钮可接受", [0.70, 0.10, 0.20, 0.08], (1920, 1080), True),
    ("超出右下边界", [0.95, 0.95, 0.2, 0.2], (1920, 1080), True),
]

failures = 0
for name, raw, size, should_pass in CASES:
    box, reason = normalize_bbox(raw, size)
    ok = (box is not None) == should_pass
    if not ok:
        failures += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name:12s} in={raw} -> {box} {reason}")

# 扩框后应当仍在图内，且不小于最小边长
small, _ = normalize_bbox([0.999, 0.001, 0.002, 0.002], (1920, 1080))
assert small, "小框应被接受"
x, y, w, h = small
assert 0 <= x and x + w <= 1.0001 and 0 <= y and y + h <= 1.0001, f"扩框越界：{small}"
assert w >= 0.027 and h >= 0.027, f"小框没扩到位：{small}"
print(f"PASS  扩框边界      -> {small}")

assert same_bbox([0.1, 0.1, 0.2, 0.2], [0.105, 0.1, 0.2, 0.2])
assert not same_bbox([0.1, 0.1, 0.2, 0.2], [0.2, 0.2, 0.2, 0.2])
print("PASS  same_bbox")

print("\n失败：", failures)
sys.exit(1 if failures else 0)
