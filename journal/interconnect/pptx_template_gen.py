#!/usr/bin/env python3
"""
AI 互联接口调研 — PowerPoint 模版生成脚本

生成一套专业的 PPTX 模版，适用于 AI 互联接口/芯片产品线调研汇报。
模版风格与 LaTeX Beamer (llm_interconnect_product_template.tex) 保持一致：
    - 主色：深蓝 (#00539F)
    - 辅色：红 (#C6262E)、绿 (#007229)、橙 (#EB6E1F)

用法:
    python pptx_template_gen.py                          → 输出 interconnect_template.pptx
    python pptx_template_gen.py -o my_template.pptx      → 指定输出路径
    python pptx_template_gen.py --demo                   → 同时生成一份填充演示数据的示例 PPTX

依赖:
    pip install python-pptx
"""

import argparse
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("错误: 需要 python-pptx 库，请运行: pip install python-pptx")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
#  配色方案 (与 Beamer 模版一致)
# ═══════════════════════════════════════════════════════════
COLOR_IE_BLUE = RGBColor(0, 83, 159)
COLOR_IE_RED = RGBColor(198, 38, 46)
COLOR_IE_GREEN = RGBColor(0, 114, 41)
COLOR_IE_ORANGE = RGBColor(235, 110, 31)
COLOR_DARK_GRAY = RGBColor(66, 66, 66)
COLOR_LIGHT_GRAY = RGBColor(230, 230, 230)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_BLUE_LIGHT_BG = RGBColor(220, 235, 250)
COLOR_GREEN_LIGHT_BG = RGBColor(220, 245, 225)
COLOR_RED_LIGHT_BG = RGBColor(250, 220, 220)

SLIDE_W = Inches(13.333)   # 16:9
SLIDE_H = Inches(7.5)

# ═══════════════════════════════════════════════════════════
#  工具函数
# ═══════════════════════════════════════════════════════════

def set_slide_bg(slide, color):
    """设置幻灯片背景色"""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color=None, line_color=None):
    """添加矩形"""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
    return shape


def add_textbox(slide, left, top, width, height, text, font_size=14,
                font_color=COLOR_DARK_GRAY, bold=False, alignment=PP_ALIGN.LEFT,
                font_name="Microsoft YaHei"):
    """添加文本框"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.color.rgb = font_color
    run.font.bold = bold
    run.font.name = font_name
    p.alignment = alignment
    return txBox


def add_paragraph(tf, text, font_size=14, font_color=COLOR_DARK_GRAY,
                  bold=False, alignment=PP_ALIGN.LEFT, font_name="Microsoft YaHei",
                  space_before=Pt(4), space_after=Pt(2)):
    """在已有 text_frame 中添加段落"""
    p = tf.add_paragraph()
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.color.rgb = font_color
    run.font.bold = bold
    run.font.name = font_name
    return p


def add_bullet_point(tf, text, level=0, font_size=13, font_color=COLOR_DARK_GRAY,
                     bold=False, bullet_char="•"):
    """添加带项目符号的段落"""
    p = tf.add_paragraph()
    p.level = level
    p.space_before = Pt(3)
    p.space_after = Pt(1)
    run = p.add_run()
    prefix = f"{bullet_char} " if level == 0 else "  "
    run.text = f"{prefix}{text}"
    run.font.size = Pt(font_size)
    run.font.color.rgb = font_color
    run.font.bold = bold
    run.font.name = "Microsoft YaHei"
    return p


def add_footer_bar(slide):
    """添加底部色条 (页脚装饰)"""
    bar = add_shape(slide, Inches(0), Inches(7.2), SLIDE_W, Inches(0.3),
                    fill_color=COLOR_IE_BLUE)


def add_top_bar(slide):
    """添加顶部色条"""
    add_shape(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.06),
              fill_color=COLOR_IE_BLUE)


def add_slide_number(slide, num, total=None):
    """添加页码"""
    text = f"{num}" if total is None else f"{num} / {total}"
    add_textbox(slide, Inches(12.0), Inches(7.15), Inches(1.2), Inches(0.3),
                text, font_size=9, font_color=COLOR_DARK_GRAY,
                alignment=PP_ALIGN.RIGHT)


def add_icon_bullet(slide, left, top, width, height, icon_text, title_text,
                    body_text, icon_color=COLOR_IE_BLUE):
    """添加带图标标题的信息卡片"""
    # 图标圆
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, Inches(0.4), Inches(0.4))
    circle.fill.solid()
    circle.fill.fore_color.rgb = icon_color
    circle.line.fill.background()
    tf = circle.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = icon_text
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_WHITE
    run.font.bold = True

    # 标题
    txBox = add_textbox(slide, left + Inches(0.5), top - Inches(0.02),
                        width, Inches(0.3),
                        title_text, font_size=12, font_color=COLOR_IE_BLUE, bold=True)
    # 正文
    txBox2 = add_textbox(slide, left + Inches(0.5), top + Inches(0.25),
                         width, height - Inches(0.3),
                         body_text, font_size=10, font_color=COLOR_DARK_GRAY)


# ═══════════════════════════════════════════════════════════
#  幻灯片构建函数
# ═══════════════════════════════════════════════════════════

def create_title_slide(prs, title, subtitle="", author=""):
    """创建标题页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_bg(slide, COLOR_WHITE)

    # 顶部大色块
    add_shape(slide, Inches(0), Inches(0), SLIDE_W, Inches(3.2),
              fill_color=COLOR_IE_BLUE)

    # 装饰条
    add_shape(slide, Inches(0), Inches(3.2), SLIDE_W, Inches(0.08),
              fill_color=COLOR_IE_ORANGE)

    # 标题
    add_textbox(slide, Inches(0.8), Inches(0.6), Inches(11.5), Inches(1.5),
                title, font_size=32, font_color=COLOR_WHITE, bold=True)

    # 副标题
    if subtitle:
        add_textbox(slide, Inches(0.8), Inches(2.0), Inches(11.5), Inches(0.8),
                    subtitle, font_size=18, font_color=RGBColor(200, 220, 240))

    # 底部信息
    y_bottom = Inches(4.0)
    if author:
        add_textbox(slide, Inches(0.8), y_bottom, Inches(5), Inches(0.5),
                    f"汇报人：{author}", font_size=14, font_color=COLOR_DARK_GRAY)

    import datetime
    today = datetime.date.today().strftime("%Y年%m月%d日")
    add_textbox(slide, Inches(0.8), y_bottom + Inches(0.45), Inches(5), Inches(0.5),
                today, font_size=12, font_color=RGBColor(120, 120, 120))

    add_footer_bar(slide)
    return slide


def create_toc_slide(prs, sections):
    """创建目录页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, COLOR_WHITE)
    add_top_bar(slide)

    # 标题
    add_textbox(slide, Inches(0.6), Inches(0.3), Inches(8), Inches(0.6),
                "汇报大纲", font_size=26, font_color=COLOR_IE_BLUE, bold=True)
    add_shape(slide, Inches(0.6), Inches(0.85), Inches(1.5), Inches(0.04),
              fill_color=COLOR_IE_ORANGE)

    # 目录项（两列布局）
    col_width = Inches(5.5)
    col_gap = Inches(0.5)
    start_x = Inches(0.8)
    start_y = Inches(1.3)
    row_h = Inches(0.55)
    items_per_col = (len(sections) + 1) // 2

    for idx, sec in enumerate(sections):
        col = idx // items_per_col
        row = idx % items_per_col
        x = start_x + col * (col_width + col_gap)
        y = start_y + row * row_h

        # 编号圆
        num_circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, x, y + Inches(0.05), Inches(0.35), Inches(0.35))
        num_circle.fill.solid()
        num_circle.fill.fore_color.rgb = COLOR_IE_BLUE
        num_circle.line.fill.background()
        tf = num_circle.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = str(idx + 1)
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_WHITE
        run.font.bold = True

        add_textbox(slide, x + Inches(0.45), y, Inches(5), Inches(0.4),
                    sec, font_size=14, font_color=COLOR_DARK_GRAY)

    add_footer_bar(slide)
    add_slide_number(slide, 1)
    return slide


def create_section_divider(prs, section_title, section_num=None):
    """创建章节分隔页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, COLOR_IE_BLUE)

    # 装饰条
    add_shape(slide, Inches(0), Inches(3.0), SLIDE_W, Inches(0.06),
              fill_color=COLOR_IE_ORANGE)

    # 章节号
    if section_num is not None:
        add_textbox(slide, Inches(0.8), Inches(2.0), Inches(2), Inches(0.6),
                    f"Part {section_num}", font_size=16,
                    font_color=RGBColor(180, 210, 240))

    # 标题
    add_textbox(slide, Inches(0.8), Inches(3.3), Inches(11), Inches(1.2),
                section_title, font_size=30, font_color=COLOR_WHITE, bold=True)

    return slide


def create_content_slide(prs, title_text):
    """创建通用内容页 (带标题栏)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, COLOR_WHITE)
    add_top_bar(slide)

    # 标题栏背景
    add_shape(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.75),
              fill_color=COLOR_BLUE_LIGHT_BG)
    add_shape(slide, Inches(0), Inches(0.75), SLIDE_W, Inches(0.04),
              fill_color=COLOR_IE_BLUE)

    # 标题文字
    add_textbox(slide, Inches(0.6), Inches(0.08), Inches(12), Inches(0.65),
                title_text, font_size=22, font_color=COLOR_IE_BLUE, bold=True)

    add_footer_bar(slide)
    return slide


def create_text_slide(prs, title, bullets, alert_text=None):
    """创建纯文字列表页"""
    slide = create_content_slide(prs, title)

    # 正文区域
    txBox = add_textbox(slide, Inches(0.8), Inches(1.1), Inches(11.5), Inches(5.5),
                        "", font_size=14)
    tf = txBox.text_frame
    tf.word_wrap = True

    for bullet in bullets:
        if isinstance(bullet, tuple):
            # (text, level, bold)
            text, level, bold = bullet
            add_bullet_point(tf, text, level=level, bold=bold)
        else:
            add_bullet_point(tf, bullet)

    # 警示框
    if alert_text:
        alert_box = add_shape(slide, Inches(0.8), Inches(5.8), Inches(11.5), Inches(0.9),
                              fill_color=COLOR_RED_LIGHT_BG)
        alert_box.line.color.rgb = COLOR_IE_RED
        alert_box.line.width = Pt(1)
        add_textbox(slide, Inches(1.0), Inches(5.9), Inches(11), Inches(0.7),
                    f"⚠ {alert_text}", font_size=13, font_color=COLOR_IE_RED, bold=False)

    return slide


def create_two_column_slide(prs, title, left_title, left_items, right_title, right_items,
                            left_alert=False, right_alert=False):
    """创建双栏对比页"""
    slide = create_content_slide(prs, title)

    col_w = Inches(5.4)
    left_x = Inches(0.8)
    right_x = Inches(6.8)

    # 左栏
    bg_color = COLOR_RED_LIGHT_BG if left_alert else COLOR_BLUE_LIGHT_BG
    box = add_shape(slide, left_x, Inches(1.1), col_w, Inches(0.45),
                    fill_color=bg_color)
    add_textbox(slide, left_x + Inches(0.15), Inches(1.12), col_w - Inches(0.3), Inches(0.4),
                left_title, font_size=14, font_color=COLOR_IE_BLUE if not left_alert else COLOR_IE_RED,
                bold=True)

    txBox = add_textbox(slide, left_x + Inches(0.15), Inches(1.65), col_w - Inches(0.3), Inches(4.8),
                        "", font_size=13)
    tf = txBox.text_frame
    tf.word_wrap = True
    for item in left_items:
        add_bullet_point(tf, item)

    # 右栏
    bg_color2 = COLOR_GREEN_LIGHT_BG if right_alert else COLOR_BLUE_LIGHT_BG
    box2 = add_shape(slide, right_x, Inches(1.1), col_w, Inches(0.45),
                     fill_color=bg_color2)
    add_textbox(slide, right_x + Inches(0.15), Inches(1.12), col_w - Inches(0.3), Inches(0.4),
                right_title, font_size=14,
                font_color=COLOR_IE_GREEN if right_alert else COLOR_IE_BLUE,
                bold=True)

    txBox2 = add_textbox(slide, right_x + Inches(0.15), Inches(1.65), col_w - Inches(0.3), Inches(4.8),
                         "", font_size=13)
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    for item in right_items:
        add_bullet_point(tf2, item)

    return slide


def create_product_slide(prs, title, specs, highlights=None):
    """创建产品规格介绍页（左文字+右高亮）"""
    slide = create_content_slide(prs, title)

    # 左侧规格列表
    txBox = add_textbox(slide, Inches(0.8), Inches(1.1), Inches(7.5), Inches(5.5),
                        "", font_size=13)
    tf = txBox.text_frame
    tf.word_wrap = True

    for key, val in specs:
        p = tf.add_paragraph()
        p.space_before = Pt(5)
        p.space_after = Pt(3)
        run_key = p.add_run()
        run_key.text = f"▸ {key}："
        run_key.font.size = Pt(13)
        run_key.font.color.rgb = COLOR_IE_BLUE
        run_key.font.bold = True
        run_key.font.name = "Microsoft YaHei"
        run_val = p.add_run()
        run_val.text = val
        run_val.font.size = Pt(13)
        run_val.font.color.rgb = COLOR_DARK_GRAY
        run_val.font.name = "Microsoft YaHei"

    # 右侧高亮框
    if highlights:
        box = add_shape(slide, Inches(8.8), Inches(1.3), Inches(4.0), Inches(4.5),
                        fill_color=COLOR_BLUE_LIGHT_BG)
        box.line.color.rgb = COLOR_IE_BLUE
        box.line.width = Pt(1.5)

        add_textbox(slide, Inches(9.0), Inches(1.4), Inches(3.6), Inches(0.4),
                    "💡 核心亮点", font_size=14, font_color=COLOR_IE_BLUE, bold=True)

        txBox2 = add_textbox(slide, Inches(9.0), Inches(1.9), Inches(3.6), Inches(3.8),
                             "", font_size=12)
        tf2 = txBox2.text_frame
        tf2.word_wrap = True
        for h in highlights:
            add_bullet_point(tf2, h, bullet_char="✦")

    return slide


def create_table_slide(prs, title, headers, rows, caption=None):
    """创建表格对比页"""
    slide = create_content_slide(prs, title)

    n_rows = len(rows) + 1  # +1 for header
    n_cols = len(headers)
    col_w = Inches(11.5 / n_cols)
    row_h = Inches(0.4)
    tbl_top = Inches(1.3)
    tbl_left = Inches(0.8)

    table_shape = slide.shapes.add_table(n_rows, n_cols,
                                         tbl_left, tbl_top,
                                         col_w * n_cols, row_h * n_rows)
    table = table_shape.table

    # 设置列宽
    for i in range(n_cols):
        table.columns[i].width = col_w

    # 表头
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_IE_BLUE
        for paragraph in cell.text_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.CENTER
            for run in paragraph.runs:
                run.font.size = Pt(11)
                run.font.color.rgb = COLOR_WHITE
                run.font.bold = True
                run.font.name = "Microsoft YaHei"

    # 数据行
    for r, row_data in enumerate(rows):
        for c, cell_text in enumerate(row_data):
            cell = table.cell(r + 1, c)
            cell.text = str(cell_text)
            # 交替行背景
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(245, 248, 252)
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_WHITE
            for paragraph in cell.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.CENTER
                for run in paragraph.runs:
                    run.font.size = Pt(10)
                    run.font.color.rgb = COLOR_DARK_GRAY
                    run.font.name = "Microsoft YaHei"

    # 图注
    if caption:
        add_textbox(slide, Inches(0.8), tbl_top + row_h * n_rows + Inches(0.2),
                    Inches(11.5), Inches(0.5),
                    caption, font_size=10, font_color=RGBColor(120, 120, 120))

    return slide


def create_summary_slide(prs, title, summary_items, conclusion_text=None):
    """创建总结页"""
    slide = create_content_slide(prs, title)

    # 核心结论卡片
    card_top = Inches(1.2)
    for i, item in enumerate(summary_items):
        x = Inches(0.6) + i * Inches(4.1)
        card = add_shape(slide, x, card_top, Inches(3.8), Inches(3.5),
                         fill_color=COLOR_BLUE_LIGHT_BG)
        card.line.color.rgb = COLOR_IE_BLUE
        card.line.width = Pt(1)

        # 编号
        num_shape = add_shape(slide, x + Inches(0.15), card_top + Inches(0.15),
                              Inches(0.5), Inches(0.5),
                              fill_color=COLOR_IE_BLUE)
        tf = num_shape.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = str(i + 1)
        run.font.size = Pt(16)
        run.font.color.rgb = COLOR_WHITE
        run.font.bold = True

        add_textbox(slide, x + Inches(0.15), card_top + Inches(0.8),
                    Inches(3.5), Inches(2.5),
                    item, font_size=11, font_color=COLOR_DARK_GRAY)

    # 底部结论
    if conclusion_text:
        conclusion_box = add_shape(slide, Inches(0.6), Inches(5.2), Inches(12.0), Inches(1.3),
                                   fill_color=RGBColor(240, 245, 250))
        conclusion_box.line.color.rgb = COLOR_IE_BLUE
        conclusion_box.line.width = Pt(1.5)
        add_textbox(slide, Inches(0.9), Inches(5.35), Inches(11.4), Inches(1.0),
                    f"📌 {conclusion_text}", font_size=14, font_color=COLOR_IE_BLUE, bold=True)

    return slide


# ═══════════════════════════════════════════════════════════
#  模版生成 (空白模版)
# ═══════════════════════════════════════════════════════════

def generate_template(output_path: str):
    """
    生成标准 PPTX 模版:
      1. 标题页
      2. 目录页
      3. 章节分隔页
      4. 纯文字列表页
      5. 双栏对比页
      6. 产品规格页
      7. 表格对比页
      8. 总结页
    """
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # ── 1. 标题页 ──
    create_title_slide(prs,
                       title="LLM 互联接口产品线调研",
                       subtitle="竞品分析 · 技术路线 · 市场定位",
                       author="葛良晨")

    # ── 2. 目录页 ──
    sections = [
        "调研背景与目标",
        "产品线总览",
        "物理层：Retimer 与 Smart Cable",
        "交换芯片与 CXL 控制器",
        "SuperNIC 与 Chiplet 互联",
        "竞争格局与市场分析",
        "总结与建议",
    ]
    create_toc_slide(prs, sections)

    # ── 3. 章节分隔页 (x7) ──
    for i, sec in enumerate(sections, 1):
        create_section_divider(prs, sec, section_num=i)

    # ── 4. 纯文字列表页 ──
    create_text_slide(prs,
                      title="调研背景",
                      bullets=[
                          "AI 大模型训练/推理对互联带宽的需求呈指数级增长",
                          "PCIe 6.0 (64 GT/s) 与 CXL 3.x 成为下一代互连标准",
                          "国产替代浪潮下，国内厂商加速布局 Retimer / Switch / CXL 芯片",
                          ("核心问题", 0, True),
                          "  • 各细分赛道的技术壁垒与市场格局如何？",
                          "  • 国产厂商的竞争定位与差异化优势在哪？",
                          "  • 未来的技术演进路线与投资机会？",
                      ],
                      alert_text="AI 集群规模从千卡向万卡演进，互联瓶颈成为系统性能的关键制约因素")

    # ── 5. 双栏对比页 ──
    create_two_column_slide(prs,
                            title="技术壁垒与市场格局",
                            left_title="🔧 硬件壁垒",
                            left_items=[
                                "SerDes IP：64 GT/s PAM4 高速串行接口设计",
                                "信号完整性验证：43 dB 链路预算下 DSP 均衡、DFE、CDR 综合调优",
                                "互操作性认证：跨 CPU/GPU/SSD/NIC 多厂商兼容性测试",
                                "PCI-SIG 合规：PCIe 6.0 认证流程复杂，周期长",
                            ],
                            right_title="🌐 生态壁垒",
                            right_items=[
                                "COSMOS 软件：Astera 的遥测/诊断/OTA 套件是真正护城河",
                                "客户绑定：Astera 已深度集成 NVIDIA/AWS/Meta 系统",
                                "先发时间差：Astera 领先 ~10 个月量产 PCIe 6.0",
                                "固件迭代：大规模部署中的 bug 修复和性能调优需要时间积累",
                            ],
                            left_alert=False, right_alert=True)

    # ── 6. 产品规格页 ──
    create_product_slide(prs,
                         title="澜起科技 M88RT61632 — 核心规格",
                         specs=[
                             ("通道数", "16 通道 PCIe 6.x / CXL 3.x Retimer"),
                             ("最大速率", "64 GT/s（自研 PAM4 SerDes）"),
                             ("链路预算", "高达 43 dB"),
                             ("封装", "354-ball FCCSP 业界主流封装"),
                             ("分叉模式", "1×16, 2×8, 4×4, 最多 8×2"),
                             ("兼容性", "向下兼容 64/32/16/8/5/2.5 GT/s"),
                             ("低功耗", "L0P / L1PM 低功耗模式"),
                             ("管理接口", "SMBus / I3C 管理 + SPI/EEPROM 固件"),
                         ],
                         highlights=[
                             "全球第 2 家推出 PCIe 6.0 Retimer",
                             "自研 64 GT/s PAM4 SerDes IP — 国内极少数掌握",
                             "链路预算 43 dB 反超 Astera (~36 dB)",
                             "2025 年营收 54.56 亿元 (+49.9% YoY)",
                         ])

    # ── 7. 表格对比页 ──
    create_table_slide(prs,
                       title="代表产品对比：澜起 vs Astera Labs vs 谱瑞",
                       headers=["指标", "澜起 M88RT61632", "Astera Aries (PCIe 6)", "谱瑞 PS8926"],
                       rows=[
                           ["速率", "64 GT/s PAM4", "64 GT/s PAM4", "32 GT/s (PCIe 5.0)"],
                           ["通道数", "16", "16", "16"],
                           ["链路预算", "高达 43 dB", "~36 dB", "~36 dB"],
                           ["协议", "PCIe 6.x / CXL 3.x", "PCIe 6.x / CXL 3.x", "PCIe 5.0 / CXL 2.0"],
                           ["SerDes", "自研 PAM4 IP", "自研 DSP", "自研"],
                           ["送样时间", "2025.01", "2024 (业界首家)", "已量产"],
                           ["低功耗", "L0P + L1PM", "低功耗设计", "支持"],
                           ["软件生态", "GUI + SDK", "COSMOS 遥测套件", "基础工具"],
                       ],
                       caption="📌 关键差距：Astera 先发 ~10 个月，COSMOS 软件生态构成最大护城河；澜起在链路预算 (43 dB) 上反超。")

    # ── 8. 总结页 ──
    create_summary_slide(prs,
                         title="总结与建议",
                         summary_items=[
                             "PCIe Retimer 市场呈现双寡头格局，Astera (86%) 与 澜起 (10.9%) 合计占 96.9%",
                             "国产替代空间巨大，但生态壁垒 (软件/客户绑定) 是最大挑战",
                             "CXL 内存池化与 AI 集群互联是未来 3-5 年高确定性增长赛道",
                         ],
                         conclusion_text="建议重点关注：澜起科技 (Retimer + CXL)、芯动科技 (交换芯片)、以及硅光/CPO 等前沿技术布局。")

    # 保存
    prs.save(output_path)
    size = Path(output_path).stat().st_size
    print(f"✅ 模版已生成: {output_path} ({size / 1024:.0f} KB)")
    print(f"   共 {len(prs.slides)} 页幻灯片")


# ═══════════════════════════════════════════════════════════
#  主入口
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="AI 互联接口调研 — PowerPoint 模版生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python pptx_template_gen.py
  python pptx_template_gen.py -o my_template.pptx
        """,
    )
    parser.add_argument("-o", "--output", default="interconnect_template.pptx",
                        help="输出的 .pptx 文件路径 (默认: interconnect_template.pptx)")

    args = parser.parse_args()
    generate_template(args.output)


if __name__ == "__main__":
    main()
