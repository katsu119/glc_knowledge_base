#!/usr/bin/env python3
"""
====================================================================
 ADC校准参考文档 —— PDF处理流水线脚本
 功能: 自动提取PDF文本、转换页面为图像、汇总文档元数据
 作者: AI辅助分析工具 (2026-05-16)
====================================================================

本脚本实现了从PDF到可分析文本/图像的完整处理流程，
用于后续对TIADC校准技术的深入分析。
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# =========================== 配置区 ===========================
# 项目根目录
PROJECT_ROOT = Path("/Users/katsu/Downloads/ADC校准参考文档")
# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "analysis_output"
# PDF文件列表
PDF_FILES = [
    "gain_loop.pdf",
    "offset__ loop.pdf",
    "time_skew__ (13).pdf",
]
# 临时图片目录
IMAGE_TMP_DIR = Path("/tmp/pdf_pages")

# =========================== 核心函数 ===========================

def check_dependencies():
    """
    检查依赖库是否安装。
    需要: PyMuPDF (fitz) 用于PDF文本提取和页面渲染。
    """
    try:
        import fitz
        print("[OK] PyMuPDF 已安装")
        return True
    except ImportError:
        print("[!] PyMuPDF 未安装，尝试安装...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pymupdf"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            print("[OK] PyMuPDF 安装成功")
            return True
        else:
            print(f"[ERROR] 安装失败: {result.stderr}")
            return False


def extract_text_from_pdf(pdf_path, output_dir):
    """
    从PDF文件中提取所有页面的文本内容。
    
    参数:
        pdf_path (Path): PDF文件路径
        output_dir (Path): 文本输出目录
    
    返回:
        dict: 包含页数、每页文本等信息的字典
    """
    import fitz

    doc = fitz.open(str(pdf_path))
    pdf_name = pdf_path.stem
    result = {
        "文件名": pdf_path.name,
        "总页数": doc.page_count,
        "页面内容": []
    }

    # 保存纯文本版本
    text_output_path = output_dir / f"{pdf_name}_text.txt"
    with open(text_output_path, "w", encoding="utf-8") as f:
        f.write(f"===== {pdf_path.name} =====\n")
        f.write(f"总页数: {doc.page_count}\n\n")

        for i, page in enumerate(doc):
            text = page.get_text()
            clean_text = text.strip() if text.strip() else "(无文本内容 - 可能为图片型PDF)"
            result["页面内容"].append({
                "页码": i + 1,
                "文本长度": len(clean_text),
                "文本摘要": clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
            })
            f.write(f"\n--- 第{i+1}页 ---\n")
            f.write(clean_text + "\n")

    doc.close()
    print(f"[OK] 文本已提取 -> {text_output_path}")
    return result


def convert_pdf_to_images(pdf_path, output_dir):
    """
    使用macOS内置sips工具将PDF页面转换为PNG图像。
    注意: sips仅能转换PDF的第一页，多页PDF需要逐页处理。
    
    参数:
        pdf_path (Path): PDF文件路径
        output_dir (Path): 图片输出目录
    
    返回:
        list: 生成的图片文件路径列表
    """
    import fitz

    pdf_name = pdf_path.stem
    image_dir = output_dir / f"{pdf_name}_images"
    image_dir.mkdir(parents=True, exist_ok=True)

    # 方法1: 使用PyMuPDF渲染所有页面为图片（更可靠）
    doc = fitz.open(str(pdf_path))
    image_paths = []
    for i, page in enumerate(doc):
        # 将页面渲染为PNG像素图 (每英寸200像素)
        pix = page.get_pixmap(dpi=200)
        img_path = image_dir / f"page_{i+1}.png"
        pix.save(str(img_path))
        image_paths.append(str(img_path))

    doc.close()
    print(f"[OK] 已转换 {len(image_paths)} 页为图片 -> {image_dir}/")
    return image_paths


def get_pdf_metadata(pdf_path):
    """
    获取PDF元数据（页数、文件大小等）。
    
    参数:
        pdf_path (Path): PDF文件路径
    
    返回:
        dict: 元数据字典
    """
    import fitz

    doc = fitz.open(str(pdf_path))
    metadata = doc.metadata
    info = {
        "文件名": pdf_path.name,
        "文件大小(MB)": round(pdf_path.stat().st_size / (1024 * 1024), 2),
        "总页数": doc.page_count,
        "标题": metadata.get("title", "无"),
        "作者": metadata.get("author", "无"),
        "主题": metadata.get("subject", "无"),
    }
    doc.close()
    return info


def process_all_pdfs():
    """
    主处理函数: 遍历所有PDF，执行完整的提取流程。
    生成汇总报告和元数据JSON文件。
    """
    print("=" * 60)
    print("  ADC校准参考文档 PDF处理流水线")
    print("=" * 60)

    # 创建输出子目录
    text_dir = OUTPUT_DIR / "extracted_text"
    image_dir = OUTPUT_DIR / "extracted_images"
    text_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    # 汇总数据
    all_metadata = []
    summary_report = []

    for pdf_name in PDF_FILES:
        pdf_path = PROJECT_ROOT / pdf_name
        if not pdf_path.exists():
            print(f"[SKIP] 文件不存在: {pdf_path}")
            continue

        print(f"\n{'─' * 50}")
        print(f"  处理: {pdf_name}")
        print(f"{'─' * 50}")

        # 1. 获取元数据
        meta = get_pdf_metadata(pdf_path)
        all_metadata.append(meta)
        print(f"  页数: {meta['总页数']}, 大小: {meta['文件大小(MB)']}MB")

        # 2. 提取文本
        text_info = extract_text_from_pdf(pdf_path, text_dir)

        # 3. 转换为图片
        images = convert_pdf_to_images(pdf_path, image_dir)

        # 4. 构建摘要
        summary = {
            "pdf文件": pdf_name,
            "页数": meta["总页数"],
            "文件大小": meta["文件大小(MB)"],
            "文本提取状态": "成功" if text_info["页面内容"] else "失败",
            "生成图片数": len(images),
            "图片路径": str(image_dir / f"{pdf_path.stem}_images"),
            "文本路径": str(text_dir / f"{pdf_path.stem}_text.txt"),
        }
        summary_report.append(summary)

    # 保存汇总报告
    report_path = OUTPUT_DIR / "pdf_processing_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "处理时间": __import__("datetime").datetime.now().isoformat(),
            "处理脚本": __file__,
            "摘要": summary_report,
            "元数据": all_metadata,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 汇总报告已保存 -> {report_path}")

    # 打印摘要表格
    print("\n" + "=" * 60)
    print("  处理完成摘要")
    print("=" * 60)
    for s in summary_report:
        print(f"  📄 {s['pdf文件']}")
        print(f"     页数: {s['页数']} | 大小: {s['文件大小']}MB")
        print(f"     文本: {s['文本提取状态']} | 图片: {s['生成图片数']}张")
    print("=" * 60)

    return summary_report


# =========================== 辅助工具函数 ===========================

def view_text_summary(pdf_name, max_pages=2):
    """
    快速查看指定PDF的文本摘要。
    
    参数:
        pdf_name (str): PDF文件名
        max_pages (int): 最多显示页数
    """
    text_path = OUTPUT_DIR / "extracted_text" / f"{Path(pdf_name).stem}_text.txt"
    if not text_path.exists():
        print(f"[ERROR] 未找到文本文件: {text_path}")
        return

    with open(text_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = content.split("--- 第")
    print(f"\n📄 {pdf_name} 文本摘要 (前{max_pages}页):")
    for i, page in enumerate(pages[1:max_pages+1], 1):
        print(f"\n  [第{i}页] {page[:300]}...")


def list_all_outputs():
    """列出所有生成的分析输出文件。"""
    print("\n📂 分析输出目录结构:")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        level = root.replace(str(OUTPUT_DIR), "").count(os.sep)
        indent = "  " * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        sub_indent = "  " * (level + 1)
        for file in files:
            file_path = Path(root) / file
            size = file_path.stat().st_size
            print(f"{sub_indent}📄 {file} ({size/1024:.1f} KB)")


# =========================== 主入口 ===========================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════╗
║        ADC校准参考文档 PDF处理流水线                   ║
║                                                     ║
║  功能:                                               ║
║    1. 提取PDF文本内容                                 ║
║    2. 将PDF页面转换为PNG图片                          ║
║    3. 生成处理汇总报告                                ║
║                                                     ║
║  使用: python pdf_processing_pipeline.py             ║
╚══════════════════════════════════════════════════════╝
    """)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 执行完整处理
    results = process_all_pdfs()

    # 列出输出
    list_all_outputs()

    print("\n✅ 所有PDF处理完成！")
