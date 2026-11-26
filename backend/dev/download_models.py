import os
import sys
import zipfile
import requests
from pathlib import Path

MODEL_DIR = Path.home() / ".EasyOCR" / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# 官方 release 地址（zip 文件，不是 raw 页面）
MODELS = [
    ("craft_mlt_25k.zip",
     "https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip",
     "craft_mlt_25k.pth"),
    ("zh_sim_g2.zip",
     "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/zh_sim_g2.zip",
     "zh_sim_g2.pth"),
    ("english_g2.zip",
     "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip",
     "english_g2.pth"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36"
}


def download(url, dst):
    print(f"下载: {url}")
    with requests.get(url, stream=True, timeout=120, headers=HEADERS, allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        with open(dst, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
                done += len(chunk)
                if total:
                    pct = done * 100 // total
                    sys.stdout.write(f"\r  进度: {pct}% ({done}/{total} bytes)")
                    sys.stdout.flush()
        print()
    size = os.path.getsize(dst)
    print(f"  文件大小: {size} bytes")
    return size


def main():
    print(f"模型目录: {MODEL_DIR}")
    ok = True
    for zip_name, url, pth_name in MODELS:
        zip_path = MODEL_DIR / zip_name
        pth_path = MODEL_DIR / pth_name
        if pth_path.exists():
            print(f"[跳过] {pth_name} 已存在")
            continue
        try:
            size = download(url, zip_path)
            if size < 100 * 1024:   # 小于 100KB 一定是错的
                print(f"[失败] {zip_name} 文件过小，不是真模型")
                zip_path.unlink(missing_ok=True)
                ok = False
                continue
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(MODEL_DIR)
            print(f"[完成] 解压 {zip_name} -> {pth_name}")
            zip_path.unlink()
        except Exception as e:
            print(f"[失败] {zip_name}: {e}")
            ok = False

    print("\n最终目录内容：")
    for p in MODEL_DIR.iterdir():
        print(f"  {p.name}  {p.stat().st_size} bytes")

    if ok:
        print("\n全部下载成功 ✓")
    else:
        print("\n有文件下载失败，看上面日志")


if __name__ == "__main__":
    main()