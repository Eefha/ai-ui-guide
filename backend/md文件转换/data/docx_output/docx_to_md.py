"""
批量把目录下的 .docx 文件转换成 .md（含图片提取）
用法：
    python docx_to_md.py "D:\\docx_files"
    python docx_to_md.py
"""
import subprocess
import sys
import shutil
from pathlib import Path


def find_pandoc():
    p = shutil.which("pandoc")
    if p:
        return p
    candidates = [
        Path.home() / "AppData" / "Local" / "Pandoc" / "pandoc.exe",
        Path("C:/Program Files/Pandoc/pandoc.exe"),
        Path("C:/Program Files (x86)/Pandoc/pandoc.exe"),
        Path("C:/pandoc/pandoc.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def convert_one(docx_path: Path, out_dir: Path, media_dir: Path, pandoc_exe: str) -> bool:
    """
    转换单个 docx 为 md。
    - md 输出到 out_dir
    - 图片提取到 media_dir
    """
    md_path = out_dir / (docx_path.stem + ".md")

    # pandoc 命令：--extract-media 会自动提取图片到指定目录
    # 图片会被放到 media_dir/docx文件名/ 下
    cmd = [
        pandoc_exe,
        str(docx_path),
        "-o", str(md_path),
        "--from", "docx",
        "--to", "markdown",
        "--standalone",
        "--extract-media", str(media_dir),
        "--wrap=none",           # 不自动换行，保持原文段落
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            size_kb = md_path.stat().st_size / 1024
            print(f"[ok]   {docx_path.name}  ->  {md_path.name}  ({size_kb:.1f} KB)")
            return True
        else:
            print(f"[fail] {docx_path.name}")
            print(f"       {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[fail] {docx_path.name}  超时")
        return False
    except Exception as e:
        print(f"[fail] {docx_path.name}  {e}")
        return False


def post_process(md_path: Path, media_root: Path):
    """
    处理图片路径：pandoc 生成的引用类似 ![](media/xxx/image1.png)
    改成相对路径 ../images/图片名
    """
    text = md_path.read_text(encoding="utf-8")

    # 找到所有图片引用，替换路径
    import re
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

    docx_stem = md_path.stem

    def replace(m):
        alt = m.group(1)
        img_path = m.group(2)

        # pandoc 可能生成 media/xxx/image1.png 这种
        # 也可能生成绝对路径
        img_name = Path(img_path).name

        # 图片已经通过 --extract-media 放在 media_root 下
        # 我们统一把图片放到 media_root 根目录，加 docx 名做前缀避免冲突
        new_name = f"{docx_stem}_{img_name}"

        # 找原始图片
        old_img = None
        for p in media_root.rglob(img_name):
            old_img = p
            break

        if old_img and old_img.exists():
            target = media_root / new_name
            if not target.exists():
                shutil.move(str(old_img), str(target))

        # 引用改为 ../images/新名
        return f"![{alt or new_name}](../images/{new_name})"

    new_text = pattern.sub(replace, text)

    # 清理 pandoc 生成的 media 子目录（已经被移走了）
    for sub in media_root.iterdir():
        if sub.is_dir():
            try:
                sub.rmdir()
            except OSError:
                pass  # 非空就算了

    md_path.write_text(new_text, encoding="utf-8")


def main():
    pandoc_exe = find_pandoc()
    if not pandoc_exe:
        print("未检测到 pandoc，请先安装：")
        print("  https://pandoc.org/installing.html")
        print("  或运行：winget install --id JohnMacFarlane.Pandoc")
        print("\n如果已经安装，请关掉当前 PowerShell，重新开一个再跑。")
        sys.exit(1)

    print(f"找到 pandoc：{pandoc_exe}")

    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if not src_dir.exists():
        print(f"目录不存在：{src_dir}")
        sys.exit(1)

    docx_files = list(src_dir.glob("*.docx"))
    # 排除 Word 打开时的临时文件（以 ~$ 开头）
    docx_files = [f for f in docx_files if not f.name.startswith("~$")]

    if not docx_files:
        print(f"{src_dir} 下没有 .docx 文件")
        sys.exit(0)

    # 输出目录
    out_dir = src_dir / "md_output"
    out_dir.mkdir(exist_ok=True)

    # 图片目录
    media_dir = out_dir / "images"
    media_dir.mkdir(exist_ok=True)

    print(f"源目录：{src_dir}")
    print(f"md 输出：{out_dir}")
    print(f"图片输出：{media_dir}")
    print(f"共 {len(docx_files)} 个文件，开始转换...\n")

    ok, fail = 0, 0
    for docx in docx_files:
        if convert_one(docx, out_dir, media_dir, pandoc_exe):
            ok += 1
            # 后处理图片路径
            md_path = out_dir / (docx.stem + ".md")
            try:
                post_process(md_path, media_dir)
            except Exception as e:
                print(f"       图片处理警告：{e}")
        else:
            fail += 1

    print(f"\n完成：成功 {ok} 个，失败 {fail} 个")
    print(f"md 输出：{out_dir}")
    print(f"图片输出：{media_dir}")


if __name__ == "__main__":
    main()