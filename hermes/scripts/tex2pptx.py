#!/usr/bin/env python3
"""
LaTeX Beamer → PPTX 转换脚本

提供两种转换模式:
  [mode=editable]  (默认) 使用 pandoc 将 .tex 转换为可编辑文本的 PPTX
  [mode=image]           将编译后的 PDF 每页渲染为高清图片嵌入 PPTX（保留原始排版）

用法:
    # 模式一：从 .tex 直接生成可编辑 PPTX（需安装 pandoc）
    python tex2pptx.py input.tex                  → input.pptx
    python tex2pptx.py input.tex output.pptx
    python tex2pptx.py input.tex --mode editable

    # 模式二：从 PDF 生成不可编辑但排版精确的 PPTX
    python tex2pptx.py input.pdf --mode image
    python tex2pptx.py input.pdf --mode image --dpi 300

依赖安装:
    pip install python-pptx Pillow pymupdf
    brew install pandoc                    # editable 模式需要
"""

import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path

# ---------- 公共依赖 ----------
try:
    from pptx import Presentation
    from pptx.util import Inches
except ImportError:
    print("错误: 需要 python-pptx 库，请运行: pip install python-pptx")
    sys.exit(1)

# ---------- 配置 ----------
DPI = 200
SLIDE_W = 10.0       # 16:9 宽 (英寸)
SLIDE_H = 5.625      # 16:9 高 (英寸)


# ==============================================================
#  模式一: Pandoc 可编辑转换
# ==============================================================
def convert_editable(tex_path: str, pptx_path: str):
    """使用 pandoc 将 .tex 转换为可编辑 PPTX"""

    if not shutil.which("pandoc"):
        print("错误: editable 模式需要 pandoc，请运行: brew install pandoc")
        print("  (或使用 --mode image 以图片方式转换)")
        sys.exit(1)

    tex_path = Path(tex_path)
    if not tex_path.exists():
        print(f"错误: 文件不存在 - {tex_path}")
        sys.exit(1)

    if not pptx_path:
        pptx_path = tex_path.with_suffix(".pptx")

    print(f"[pandoc] 正在转换: {tex_path} → {pptx_path}")

    # 构建 pandoc 命令
    # -f latex: 输入格式
    # -t pptx:  输出格式
    # --pdf-engine=xelatex: 如需处理中文等
    cmd = [
        "pandoc",
        str(tex_path),
        "-o", str(pptx_path),
        "-f", "latex",
        "-t", "pptx",
        "--pdf-engine=xelatex",
        "--slide-level=2",            # section 为一级, frame 为二级
        "-V", "aspectratio=169",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        size = Path(pptx_path).stat().st_size
        print(f"✅ 转换成功！输出: {pptx_path} ({size/1024:.0f} KB)")
        print("   PPTX 中的文本为可编辑状态。")
        print("   注意: beamer 特有元素（TikZ、overlay、columns 等）可能无法完美转换。")
    else:
        print(f"❌ pandoc 转换失败 (返回码 {result.returncode})")
        if result.stderr:
            print("错误信息:")
            for line in result.stderr.strip().splitlines()[-20:]:
                print(f"  {line}")
        print("\n建议: 先编译为 PDF，再使用 --mode image 以图片方式转换。")
        sys.exit(1)


# ==============================================================
#  模式二: PDF → 图片 → PPTX (保留原始排版)
# ==============================================================
def convert_image(pdf_path: str, pptx_path: str, dpi: int = DPI):
    """将 PDF 每页渲染为图片嵌入 PPTX (保留精确排版，但不可编辑文本)"""

    try:
        import fitz
    except ImportError:
        print("错误: image 模式需要 PyMuPDF 库，请运行: pip install pymupdf")
        sys.exit(1)

    try:
        from PIL import Image
    except ImportError:
        print("错误: 需要 Pillow 库，请运行: pip install Pillow")
        sys.exit(1)

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"错误: 文件不存在 - {pdf_path}")
        sys.exit(1)

    if not pptx_path:
        pptx_path = pdf_path.with_suffix(".pptx")

    print(f"[1/3] 正在打开 PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    print(f"     共 {num_pages} 页")

    print(f"[2/3] 正在渲染图片 (DPI={dpi}) ...")
    image_paths = []
    for i in range(num_pages):
        page = doc[i]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_path = pdf_path.parent / f"._slide_{i:04d}.png"
        pix.save(str(img_path))
        image_paths.append(img_path)
        print(f"     第 {i+1}/{num_pages} 页")
    doc.close()

    print(f"[3/3] 正在创建 PPTX: {pptx_path}")
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    blank_layout = prs.slide_layouts[6]

    for idx, img_path in enumerate(image_paths):
        slide = prs.slides.add_slide(blank_layout)
        with Image.open(img_path) as img:
            img_w, img_h = img.size
        sw = prs.slide_width
        sh = prs.slide_height
        scale = min(sw / img_w, sh / img_h)
        dw = int(img_w * scale)
        dh = int(img_h * scale)
        left = int((sw - dw) / 2)
        top = int((sh - dh) / 2)
        slide.shapes.add_picture(str(img_path), left, top, width=dw, height=dh)
        print(f"     第 {idx+1}/{num_pages} 页已嵌入")

    prs.save(str(pptx_path))
    print(f"\n✅ 转换完成！输出: {pptx_path}")
    for p in image_paths:
        p.unlink()
    print("   临时图片已清理")


# ==============================================================
#  主入口: 自动判断输入类型 + 命令行参数
# ==============================================================
def main():
    parser = argparse.ArgumentParser(
        description="LaTeX Beamer → PPTX 转换 (支持可编辑文本 / 图片精确排版两种模式)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 可编辑模式 (从 .tex 直接转换，需 pandoc)
  %(prog)s main.tex
  %(prog)s main.tex --mode editable

  # 图片模式 (从 PDF 转换，保留原始排版)
  %(prog)s main.pdf --mode image
  %(prog)s main.pdf --mode image --dpi 300

工作流建议:
  1. 如需编辑文本 → 用 editable 模式 (pandoc)
  2. 如需精确排版 → 先编译 PDF, 再用 image 模式
        """,
    )
    parser.add_argument("input", help="输入的 .tex 或 .pdf 文件路径")
    parser.add_argument("output", nargs="?", default=None, help="输出的 .pptx 文件路径 (可选)")
    parser.add_argument(
        "--mode", choices=["auto", "editable", "image"], default="auto",
        help="转换模式: auto=自动推断, editable=可编辑文本, image=图片精确排版 (默认: auto)"
    )
    parser.add_argument("--dpi", type=int, default=DPI,
                        help=f"图片渲染分辨率 (默认: {DPI}, image 模式有效)")

    args = parser.parse_args()
    input_path = Path(args.input)

    # 自动推断模式
    mode = args.mode
    if mode == "auto":
        ext = input_path.suffix.lower()
        if ext == ".tex":
            mode = "editable"
            print("→ 检测到 .tex 文件，使用 editable 模式 (可编辑文本)")
        elif ext == ".pdf":
            mode = "image"
            print("→ 检测到 .pdf 文件，使用 image 模式 (图片精确排版)")
        else:
            print(f"错误: 不支持的文件格式 '{ext}'，请使用 .tex 或 .pdf")
            sys.exit(1)

    if mode == "editable":
        convert_editable(args.input, args.output)
    else:
        convert_image(args.input, args.output, dpi=args.dpi)


if __name__ == "__main__":
    main()
