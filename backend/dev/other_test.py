"""
独立的 OCR 测试脚本，不依赖项目其他代码。
用法：python test_ocr.py 图片1.png
"""
import os
import sys
import io
import json
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# 加载 .env
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

print("=" * 60)
print("步骤 1：检查环境变量")
print("=" * 60)

ak_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
ak_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

print(f"ALIBABA_CLOUD_ACCESS_KEY_ID    : {ak_id if ak_id else '❌ 未设置'}")
print(f"ALIBABA_CLOUD_ACCESS_KEY_SECRET: {'✅ 已设置' if ak_secret else '❌ 未设置'}")
print(f".env 文件路径: {ENV_PATH}")
print(f".env 是否存在: {ENV_PATH.exists()}")

if not ak_id or not ak_secret:
    print("\n❌ 环境变量未读取到，停止测试。")
    print("请检查 .env 文件内容，格式：")
    print("  ALIBABA_CLOUD_ACCESS_KEY_ID=你的ID")
    print("  ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的Secret")
    sys.exit(1)

print("\n" + "=" * 60)
print("步骤 2：检查图片")
print("=" * 60)

img_path = sys.argv[1] if len(sys.argv) > 1 else "图片1.png"
if not os.path.exists(img_path):
    print(f"❌ 图片不存在: {img_path}")
    sys.exit(1)

img = Image.open(img_path)
print(f"图片路径: {img_path}")
print(f"图片尺寸: {img.size}")
print(f"图片模式: {img.mode}")

print("\n" + "=" * 60)
print("步骤 3：初始化阿里云 OCR 客户端")
print("=" * 60)

try:
    from alibabacloud_ocr_api20210707.client import Client as OcrClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_ocr_api20210707 import models as ocr_models
    from alibabacloud_tea_util import models as util_models

    config = open_api_models.Config(
        access_key_id=ak_id,
        access_key_secret=ak_secret,
    )
    config.endpoint = "ocr-api.cn-hangzhou.aliyuncs.com"
    client = OcrClient(config)
    print("✅ 客户端初始化成功")
    print(f"Endpoint: {config.endpoint}")
except Exception as e:
    print(f"❌ 客户端初始化失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("步骤 4：调用 OCR API")
print("=" * 60)

try:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    print(f"图片字节数: {len(img_bytes)}")

    request = ocr_models.RecognizeGeneralRequest(body=img_bytes)
    runtime = util_models.RuntimeOptions()

    print("正在调用 API...")
    response = client.recognize_general_with_options(request, runtime)

    print("✅ API 调用成功")
    print(f"Response body 类型: {type(response.body)}")
    print(f"Response body: {response.body}")

except Exception as e:
    print(f"❌ API 调用失败")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("步骤 5：解析结果")
print("=" * 60)

try:
    result = response.body
    if not result or not result.data:
        print("❌ 返回结果为空")
        sys.exit(1)

    data = json.loads(result.data)
    print(f"data 顶层 keys: {list(data.keys())}")

    if "prism_wordsInfo" in data:
        words = data["prism_wordsInfo"]
        print(f"✅ 识别到 {len(words)} 个文字")
        print("\n前 5 个识别结果：")
        for w in words[:5]:
            text = w.get("word", "")
            pos = w.get("pos", [])
            if pos:
                x = pos[0].get("x", 0)
                y = pos[0].get("y", 0)
                print(f"  - 文字：'{text}'  位置：({x}, {y})")
    else:
        print(f"⚠️ 未找到 prism_wordsInfo 字段")
        print(f"完整 data: {json.dumps(data, ensure_ascii=False)[:500]}")

except Exception as e:
    print(f"❌ 解析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 测试全部通过")
print("=" * 60)