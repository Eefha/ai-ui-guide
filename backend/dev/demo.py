"""
批量把目录下的 .md 文件转换成 .docx
用法：
    python md_to_docx.py "D:d_files"       # 指定目录
    python md_to_docx.py                      # 转换当前目录
"""
import subprocess
import sys
from pathlib import Path


def check_pandoc():
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False


def convert_one(md_path: Path, out_dir: Path) -> bool:
    docx_path = out_dir / (md_path.stem + ".docx")

    cmd = [
        "pandoc",
        str(md_path),
        "-o", str(docx_path),
        "--from", "markdown",
        "--to", "docx",
        "--standalone",
        "--resource-path", str(md_path.parent),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            size_kb = docx_path.stat().st_size / 1024
            print(f"[ok]   {md_path.name}  ->  {docx_path.name}  ({size_kb:.1f} KB)")
            return True
        else:
            print(f"[fail] {md_path.name}")
            print(f"       {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[fail] {md_path.name}  超时")
        return False
    except Exception as e:
        print(f"[fail] {md_path.name}  {e}")
        return False


def main():
    if not check_pandoc():
        print("未检测到 pandoc，请先安装：")
        print("  https://pandoc.org/installing.html")
        print("  或运行：winget install --id JohnMacFarlane.Pandoc")
        sys.exit(1)

    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if not src_dir.exists():
        print(f"目录不存在：{src_dir}")
        sys.exit(1)

    md_files = list(src_dir.glob("*.md"))
    if not md_files:
        print(f"{src_dir} 下没有 .md 文件")
        sys.exit(0)

    out_dir = src_dir / "docx_output"
    out_dir.mkdir(exist_ok=True)

    print(f"源目录：{src_dir}")
    print(f"输出目录：{out_dir}")
    print(f"共 {len(md_files)} 个文件，开始转换...\n")

    ok, fail = 0, 0
    for md in md_files:
        if convert_one(md, out_dir):
            ok += 1
        else:
            fail += 1

    print(f"\n完成：成功 {ok} 个，失败 {fail} 个")
    print(f"输出目录：{out_dir}")


if __name__ == "__main__":
    main()