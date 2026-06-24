#!/usr/bin/env python3
"""
Astera Labs 全面调研 — PPTX 生成脚本

以 Astera Labs 为调研中心，按四大产品线 (Aries / Leo / Scorpio / Taurus) 为框架：
  Part 1: Astera Labs 公司背景
  Part 2: 四大产品线总览
  Part 3: Aries — PCIe/CXL 智能重定时器
  Part 4: Leo — CXL 智能内存控制器
  Part 5: Scorpio — 智能 Fabric 交换芯片
  Part 6: Taurus — 以太网智能线缆模块
  Part 7: COSMOS 软件平台与生态壁垒
  Part 8: 竞争格局总结

参考来源:
  - alab调研.pptx (产品框架)
  - asteralabs_report.tex / asteralabs_presentation.tex (详细调研)
  - llm_interconnect_product_template.tex (竞争产品对比)
  - cxl_presentation.tex (CXL 产品)
  - xconn_presentation.tex (XConn 交换芯片)

用法:
    python pptx_astera.py                          → 输出 asteralabs_research.pptx
    python pptx_astera.py -o final.pptx

依赖:
    pip install python-pptx
"""

import argparse
import sys
import datetime
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("错误: 需要 python-pptx 库，请运行: pip install python-pptx")
    sys.exit(1)

# 图片资源根目录 (相对于脚本所在目录)
SCRIPT_DIR = Path(__file__).resolve().parent
IMG_DIR = SCRIPT_DIR  # interconnect 目录下有主图片
FIGS_DIR = SCRIPT_DIR / "figs"

# ═══════════════════════ 配色 ═══════════════════════
COLOR_BLUE   = RGBColor(0, 83, 159)
COLOR_RED    = RGBColor(198, 38, 46)
COLOR_GREEN  = RGBColor(0, 114, 41)
COLOR_ORANGE = RGBColor(235, 110, 31)
COLOR_GOLD   = RGBColor(200, 150, 0)
COLOR_DARK   = RGBColor(66, 66, 66)
COLOR_WHITE  = RGBColor(255, 255, 255)
COLOR_BLUE_BG   = RGBColor(220, 235, 250)
COLOR_GREEN_BG  = RGBColor(220, 245, 225)
COLOR_RED_BG    = RGBColor(250, 220, 220)
COLOR_ORANGE_BG = RGBColor(255, 240, 220)
COLOR_GOLD_BG   = RGBColor(255, 250, 230)

SW = Inches(13.333); SH = Inches(7.5)

# ═══════════════════════ 工具函数 ═══════════════════════

def bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def rect(slide, l, t, w, h, fill=None, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    s.line.fill.background()
    if fill: s.fill.solid(); s.fill.fore_color.rgb = fill
    if line: s.line.color.rgb = line; s.line.width = Pt(1)
    return s

def tb(slide, l, t, w, h, text, fs=14, fc=COLOR_DARK, bold=False, align=PP_ALIGN.LEFT):
    tx = slide.shapes.add_textbox(l, t, w, h)
    tf = tx.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(fs); r.font.color.rgb = fc; r.font.bold = bold; r.font.name = "Microsoft YaHei"
    return tx

def para(tf, text, fs=13, fc=COLOR_DARK, bold=False, sb=Pt(4)):
    p = tf.add_paragraph(); p.space_before = sb
    r = p.add_run(); r.text = text
    r.font.size = Pt(fs); r.font.color.rgb = fc; r.font.bold = bold; r.font.name = "Microsoft YaHei"

def bullet(tf, text, level=0, fs=12, fc=COLOR_DARK, bold=False, ch="•"):
    p = tf.add_paragraph(); p.level = level; p.space_before = Pt(2)
    r = p.add_run()
    prefix = f"{ch} " if level == 0 else f"  {ch} "
    r.text = f"{prefix}{text}"
    r.font.size = Pt(fs); r.font.color.rgb = fc; r.font.bold = bold; r.font.name = "Microsoft YaHei"

def footer(slide): rect(slide, Inches(0), Inches(7.2), SW, Inches(0.3), fill=COLOR_BLUE)
def topbar(slide): rect(slide, Inches(0), Inches(0), SW, Inches(0.06), fill=COLOR_BLUE)

def img(slide, filename, l, t, w=None, h=None):
    """添加图片: 支持主目录、figs子目录, 自动按比例缩放"""
    path = IMG_DIR / filename
    if not path.exists():
        path = FIGS_DIR / filename
    if not path.exists():
        print(f"  ⚠ 图片未找到: {filename}, 跳过")
        return None
    # 获取原始尺寸
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    # 自动计算宽/高以保持比例
    if w is not None and h is None:
        h = w * ih / iw
    elif h is not None and w is None:
        w = h * iw / ih
    elif w is None and h is None:
        w = Inches(3); h = w * ih / iw
    return slide.shapes.add_picture(str(path), l, t, width=w, height=h)

def _header(slide, title, accent=COLOR_BLUE):
    topbar(slide)
    rect(slide, Inches(0), Inches(0), SW, Inches(0.75), fill=COLOR_BLUE_BG)
    rect(slide, Inches(0), Inches(0.75), SW, Inches(0.04), fill=accent)
    tb(slide, Inches(0.6), Inches(0.08), Inches(12), Inches(0.65),
       title, fs=22, fc=COLOR_BLUE, bold=True)
    footer(slide)

# ═══════════════════════ 幻灯片构建 ═══════════════════════

def make_title(prs, title, subtitle="", author="葛良晨"):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, COLOR_WHITE)
    rect(s, Inches(0), Inches(0), SW, Inches(3.2), fill=COLOR_BLUE)
    rect(s, Inches(0), Inches(3.2), SW, Inches(0.08), fill=COLOR_GOLD)
    tb(s, Inches(0.8), Inches(0.6), Inches(11.5), Inches(1.5), title, fs=32, fc=COLOR_WHITE, bold=True)
    if subtitle:
        tb(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(0.8), subtitle, fs=18,
           fc=RGBColor(200, 220, 240))
    tb(s, Inches(0.8), Inches(4.0), Inches(5), Inches(0.5),
       f"汇报人：{author}", fs=14, fc=COLOR_DARK)
    tb(s, Inches(0.8), Inches(4.45), Inches(5), Inches(0.5),
       datetime.date.today().strftime("%Y年%m月%d日"), fs=12, fc=RGBColor(120, 120, 120))
    footer(s)

def make_toc(prs, sections):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, COLOR_WHITE); topbar(s)
    tb(s, Inches(0.6), Inches(0.3), Inches(8), Inches(0.6), "汇报大纲", fs=26, fc=COLOR_BLUE, bold=True)
    rect(s, Inches(0.6), Inches(0.85), Inches(1.5), Inches(0.04), fill=COLOR_GOLD)
    ipc = (len(sections) + 1) // 2
    for i, sec in enumerate(sections):
        c = i // ipc; r = i % ipc
        x = Inches(0.8) + c * Inches(6.0); y = Inches(1.3) + r * Inches(0.55)
        nc = s.shapes.add_shape(MSO_SHAPE.OVAL, x, y + Inches(0.05), Inches(0.32), Inches(0.32))
        nc.fill.solid(); nc.fill.fore_color.rgb = COLOR_BLUE; nc.line.fill.background()
        tf = nc.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        rn = p.add_run(); rn.text = str(i + 1); rn.font.size = Pt(10)
        rn.font.color.rgb = COLOR_WHITE; rn.font.bold = True
        tb(s, x + Inches(0.4), y, Inches(5), Inches(0.35), sec, fs=13, fc=COLOR_DARK)
    footer(s)

def make_div(prs, title, num=None, label="Part"):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, COLOR_BLUE)
    rect(s, Inches(0), Inches(3.0), SW, Inches(0.06), fill=COLOR_GOLD)
    if num:
        tb(s, Inches(0.8), Inches(1.8), Inches(3), Inches(0.5),
           f"{label} {num}", fs=16, fc=RGBColor(180, 210, 240))
    tb(s, Inches(0.8), Inches(3.3), Inches(11), Inches(1.2), title, fs=30, fc=COLOR_WHITE, bold=True)

def make_text(prs, title, bullets, alert=None):
    s = prs.slides.add_slide(prs.slide_layouts[6]); _header(s, title)
    tx = tb(s, Inches(0.8), Inches(1.05), Inches(11.5), Inches(5.5), "")
    tf = tx.text_frame; tf.word_wrap = True
    for b in bullets:
        if isinstance(b, tuple):
            text, level, bold = b; bullet(tf, text, level=level, bold=bold)
        elif b.startswith("##"):
            para(tf, b[2:].strip(), fs=14, fc=COLOR_BLUE, bold=True, sb=Pt(10))
        else:
            bullet(tf, b)
    if alert:
        bx = rect(s, Inches(0.8), Inches(5.85), Inches(11.5), Inches(0.85), fill=COLOR_RED_BG)
        bx.line.color.rgb = COLOR_RED
        tb(s, Inches(1.0), Inches(5.95), Inches(11), Inches(0.65),
           f"⚠ {alert}", fs=12, fc=COLOR_RED)
    return s

def make_two(prs, title, lt, li, rt, ri, la=False, ra=False):
    s = prs.slides.add_slide(prs.slide_layouts[6]); _header(s, title)
    cw = Inches(5.4); lx = Inches(0.8); rx = Inches(6.8)
    cl = COLOR_RED_BG if la else COLOR_BLUE_BG
    fl = COLOR_RED if la else COLOR_BLUE
    rect(s, lx, Inches(1.1), cw, Inches(0.45), fill=cl)
    tb(s, lx + Inches(0.15), Inches(1.12), cw, Inches(0.4), lt, fs=13, fc=fl, bold=True)
    ltx = tb(s, lx + Inches(0.15), Inches(1.65), cw - Inches(0.3), Inches(4.8), "")
    for it in li: bullet(ltx.text_frame, it, fs=12)
    cr = COLOR_GREEN_BG if ra else COLOR_BLUE_BG
    fr = COLOR_GREEN if ra else COLOR_BLUE
    rect(s, rx, Inches(1.1), cw, Inches(0.45), fill=cr)
    tb(s, rx + Inches(0.15), Inches(1.12), cw, Inches(0.4), rt, fs=13, fc=fr, bold=True)
    rtx = tb(s, rx + Inches(0.15), Inches(1.65), cw - Inches(0.3), Inches(4.8), "")
    for it in ri: bullet(rtx.text_frame, it, fs=12)
    return s

def make_prod(prs, title, specs, highlights=None, note=None, accent=COLOR_BLUE):
    """产品规格页"""
    s = prs.slides.add_slide(prs.slide_layouts[6]); _header(s, title, accent)
    tx = tb(s, Inches(0.8), Inches(1.1), Inches(7.5), Inches(5.5), "")
    tf = tx.text_frame; tf.word_wrap = True
    for k, v in specs:
        p = tf.add_paragraph(); p.space_before = Pt(4); p.space_after = Pt(2)
        rk = p.add_run(); rk.text = f"▸ {k}："; rk.font.size = Pt(12)
        rk.font.color.rgb = accent; rk.font.bold = True; rk.font.name = "Microsoft YaHei"
        rv = p.add_run(); rv.text = v; rv.font.size = Pt(12)
        rv.font.color.rgb = COLOR_DARK; rv.font.name = "Microsoft YaHei"
    if highlights:
        bx = rect(s, Inches(8.8), Inches(1.3), Inches(4.0), Inches(3.5), fill=COLOR_BLUE_BG)
        bx.line.color.rgb = accent; bx.line.width = Pt(1.5)
        tb(s, Inches(9.0), Inches(1.4), Inches(3.6), Inches(0.4),
           "💡 核心卖点", fs=13, fc=accent, bold=True)
        htx = tb(s, Inches(9.0), Inches(1.9), Inches(3.6), Inches(2.8), "")
        for h in highlights: bullet(htx.text_frame, h, ch="✦", fs=11)
    if note:
        nb = rect(s, Inches(8.8), Inches(5.1), Inches(4.0), Inches(1.4), fill=COLOR_RED_BG)
        nb.line.color.rgb = COLOR_RED
        tb(s, Inches(9.0), Inches(5.2), Inches(3.6), Inches(1.2), note, fs=10, fc=COLOR_RED)
    return s

def make_prod_dual(prs, title, left_items, right_items, accent=COLOR_BLUE, left_tag="🔧", right_tag="⚡"):
    """产品双栏：左=规格/定义, 右=高级特性/亮点"""
    s = prs.slides.add_slide(prs.slide_layouts[6]); _header(s, title, accent)
    cw = Inches(5.4); lx = Inches(0.8); rx = Inches(6.8)
    rect(s, lx, Inches(1.1), cw, Inches(0.45), fill=COLOR_BLUE_BG)
    tb(s, lx + Inches(0.15), Inches(1.12), cw, Inches(0.4),
       f"{left_tag} 产品定义与规格", fs=13, fc=accent, bold=True)
    ltx = tb(s, lx + Inches(0.15), Inches(1.65), cw - Inches(0.3), Inches(4.8), "")
    for it in left_items: bullet(ltx.text_frame, it, fs=12)
    rect(s, rx, Inches(1.1), cw, Inches(0.45), fill=COLOR_GREEN_BG)
    tb(s, rx + Inches(0.15), Inches(1.12), cw, Inches(0.4),
       f"{right_tag} 高级特性", fs=13, fc=COLOR_GREEN, bold=True)
    rtx = tb(s, rx + Inches(0.15), Inches(1.65), cw - Inches(0.3), Inches(4.8), "")
    for it in right_items: bullet(rtx.text_frame, it, fs=12, ch="✦")
    return s

def make_table(prs, title, headers, rows, caption=None, small_fs=False):
    s = prs.slides.add_slide(prs.slide_layouts[6]); _header(s, title)
    nr = len(rows) + 1; nc = len(headers)
    cw = Inches(11.5 / nc); rh = Inches(0.36)
    ttop = Inches(1.25); tleft = Inches(0.8)
    ts = s.shapes.add_table(nr, nc, tleft, ttop, cw * nc, rh * nr)
    tbl = ts.table
    for i in range(nc): tbl.columns[i].width = cw
    for i, h in enumerate(headers):
        c = tbl.cell(0, i); c.text = h; c.fill.solid()
        c.fill.fore_color.rgb = COLOR_BLUE
        for pg in c.text_frame.paragraphs:
            pg.alignment = PP_ALIGN.CENTER
            for rn in pg.runs: rn.font.size = Pt(10); rn.font.color.rgb = COLOR_WHITE; rn.font.bold = True
    font_sz = 9 if small_fs else 10
    for r, row in enumerate(rows):
        for ci, txt in enumerate(row):
            c = tbl.cell(r + 1, ci); c.text = str(txt); c.fill.solid()
            c.fill.fore_color.rgb = RGBColor(245, 248, 252) if r % 2 == 0 else COLOR_WHITE
            for pg in c.text_frame.paragraphs:
                pg.alignment = PP_ALIGN.CENTER
                for rn in pg.runs: rn.font.size = Pt(font_sz); rn.font.color.rgb = COLOR_DARK
    if caption:
        tb(s, Inches(0.8), ttop + rh * nr + Inches(0.15), Inches(11.5), Inches(0.4),
           caption, fs=9, fc=RGBColor(120, 120, 120))
    return s

def make_end(prs, author="葛良晨"):
    s = prs.slides.add_slide(prs.slide_layouts[6]); bg(s, COLOR_BLUE)
    rect(s, Inches(0), Inches(3.0), SW, Inches(0.06), fill=COLOR_GOLD)
    tb(s, Inches(0), Inches(2.2), SW, Inches(1.5), "谢谢！欢迎提问", fs=36,
       fc=COLOR_WHITE, bold=True, align=PP_ALIGN.CENTER)
    tb(s, Inches(0), Inches(3.8), SW, Inches(0.8), author, fs=20,
       fc=RGBColor(180, 210, 240), align=PP_ALIGN.CENTER)
    tb(s, Inches(0), Inches(4.4), SW, Inches(0.6),
       datetime.date.today().strftime("%Y年%m月%d日"), fs=14,
       fc=RGBColor(150, 190, 220), align=PP_ALIGN.CENTER)

# ═══════════════════════ 主构建 ═══════════════════════

def build(output_path):
    prs = Presentation(); prs.slide_width = SW; prs.slide_height = SH

    # ━━━━ 标题 ━━━━
    make_title(prs,
        "Astera Labs 全面调研报告",
        "四大产品线 (Aries / Leo / Scorpio / Taurus) · 竞争分析 · 市场定位",
        "葛良晨")

    sections = [
        "Astera Labs 公司背景",
        "四大产品线总览",
        "Aries — PCIe/CXL 智能重定时器",
        "Leo — CXL 智能内存控制器",
        "Scorpio — 智能 Fabric 交换芯片",
        "Taurus — 以太网智能线缆模块",
        "COSMOS 软件平台与生态壁垒",
        "竞争格局总结",
    ]
    make_toc(prs, sections)

    # ====== Part 1: Astera Labs 公司背景 ======
    make_div(prs, "Astera Labs 公司背景", 1)

    make_text(prs, "Astera Labs 公司概览",
        bullets=[
            "##基本信息",
            "成立: 2017年, Santa Clara CA → 2025年迁至 San Jose",
            "IPO: 2024年3月 Nasdaq: ALAB, 估值 ~$5.5B, 募资 ~$713M",
            "商业模式: Fabless 半导体设计公司 (TSMC 代工)",
            "三位创始人全部来自 Texas Instruments (TI) — 模拟/混合信号设计深厚积累",
            "##创始人基因 (TI 铁三角)",
            "Jitendra Mohan (CEO) + Sanjay Gajendra + Casey Morrison",
            "三人在 TI 共事后观察到数据中心连接技术无法跟上 AI/ML 发展步伐",
            "在 Sanjay Gajendra 的车库中开始创业",
            "获 2026 年度安永全球企业家大奖 (EY World Entrepreneur Of The Year)",
        ],
        alert="核心定位: 「Purpose-Built Connectivity for Rack-Scale AI」— 专为机架级 AI 构建的连接方案供应商")
    # 图片: Astera 架构概览
    img(prs.slides[-1], "astera_arch.png", Inches(8.5), Inches(2.8), w=Inches(4.5))

    make_text(prs, "融资历程与 IPO",
        bullets=[
            "##融资历程",
            "Series B (2020.04): Intel Capital, Sutter Hill Ventures 等",
            "Series C (2021.09): $50M, Fidelity 领投, 估值 ~$950M",
            "Series D (2022.11): $150M, 估值超 $3B",
            "IPO (2024.03): $713M, Morgan Stanley & JPMorgan 承销, 估值 ~$5.5B",
            "##关键事件",
            "IPO 前曾拒绝 Marvell 收购要约",
            "Intel Capital 为早期投资方 — Intel 是 PCIe/CXL 标准核心推动者",
            "Post-IPO: 扩展台湾/印度/以色列研发中心, 加入 Arm Total Design 生态",
        ])

    make_text(prs, "核心定位：三层架构",
        bullets=[
            "##定位层次",
            "物理层: Aries Retimer / Smart Cable — 解决高速信号完整性问题",
            "架构层: Scorpio Fabric Switch — GPU/NIC/Storage 交换互连",
            "系统层: COSMOS — Telemetry & Fleet Management 统一管理平台",
            "##核心差异化",
            "开放标准 (PCIe/CXL/Ethernet) vs 私有协议 (NVLink)",
            "「连接的中立国 (Switzerland of Connectivity)」定位",
            "不与 GPU 厂商直接竞争，充当 AI Infra 连接层供应商",
            "三类 IP 支柱: SerDes/DSP IP + Switching Fabric IP + CXL Protocol IP",
            "COSMOS 是软件粘合剂，将所有硬件统一到单一管理平台",
        ])

    make_two(prs,
        "财务表现 (FY2025)",
        "📊 收入增长轨迹",
        ["Q1 2025: $159.4M",
         "Q2 2025: $191.9M (+20%)",
         "Q3 2025: $230.6M (+20%)",
         "Q4 2025: $270.6M (+17%)",
         "FY2025 全年: $852.5M (+93% YoY)",
         "Q1 2026: $308.4M (+93% YoY) → 年化 ~$1.23B",
         "3年间收入增长约 10 倍, 由 AI DC 建设推动"],
        "💰 利润率与估值",
        ["FY2025 毛利率: 75.7% (接近 NVIDIA 水平)",
         "FY2025 净利润: $219.1M (净利率 25.7%)",
         "Q1 2026 毛利率: 76.2%",
         "",
         "行业对比:",
         "  NVIDIA 75-78%, Broadcom 65-70%",
         "  Credo ~60%, Marvell ~60%+",
         "",
         "⚠ 客户集中度: 推测前2-3大客户占总收入 >50%"],
        ra=True)

    # ====== Part 2: 四大产品线总览 ======
    make_div(prs, "四大产品线总览", 2)

    make_table(prs,
        "Astera Labs 全产品线 (星座系列)",
        ["产品", "类型", "协议/标准", "核心价值", "目标场景"],
        [
            ["Aries Retimer", "Smart DSP Retimer", "PCIe 6 / CXL 3.x", "信号再生, DSP 均衡, 43 dB", "AI 服务器, AEC, 存储"],
            ["Aries Smart Cable", "Active Cable Module", "PCIe 6 / CXL 3.x", "7m 铜缆, 64 GT/s", "机架内 GPU-NIC 互联"],
            ["Leo", "CXL Memory Controller", "CXL 3.1", "DDR5 内存扩展/池化, max 2TB", "内存池化, KV Cache"],
            ["Scorpio P-Series", "Smart Fabric Switch", "PCIe 6", "PCIe Fabric, 32-320 lanes", "GPU/存储资源池化"],
            ["Scorpio X-Series", "Smart Fabric Switch", "Memory Semantic", "GPU Scale-Up Fabric, Hypercast™", "万卡级 GPU 集群"],
            ["Taurus", "Active Cable Module", "Ethernet", "800G per link, 7m, <100ns", "ToR-NIC, Scale-Out"],
            ["COSMOS", "Software Platform", "—", "Telemetry, Fleet Mgmt, RAS", "全硬件统一管理"],
        ],
        caption="产品战略: 从 Aries (物理层 DSP) → Scorpio (交换) → Leo (内存) → Taurus (以太网) 的平台扩展策略")

    make_text(prs, "产品之间的战略关系：平台扩展",
        bullets=[
            "##技术核心 → 三个 IP 支柱",
            "SerDes/DSP IP: Aries 系列基础 (解决信号完整性问题)",
            "Switching Fabric IP: Scorpio 系列基础 (解决多节点路由问题)",
            "CXL Protocol IP: Leo 基础 (解决内存解耦问题)",
            "##产品演进路线",
            "Aries Retimer → 物理层基础, 所有高速信号都需要",
            "Aries Smart Cable → 将 Retimer 集成到 cable paddle card, 实现智能电缆",
            "Scorpio P-Series → 从 Retimer 向上扩展到交换, 利用同一 PCIe 6 物理层",
            "Scorpio X-Series → 从标准 PCIe 扩展到 memory-semantic, 进入 GPU scale-up",
            "Leo → 从连接扩展到内存, 利用 CXL 协议做内存扩展/池化",
            "Taurus → 从 PCIe 扩展到 Ethernet (scale-out), 覆盖数据中心另一大连接领域",
            "COSMOS → 将所有硬件统一管理, 软件粘合剂",
        ])

    # ====== Part 3: Aries ======
    make_div(prs, "Aries — PCIe/CXL 智能重定时器与智能线缆", 3)

    make_prod_dual(prs,
        "Aries Smart DSP Retimer — 产品定义与技术架构",
        ["PCIe 6.x / CXL 3.x 智能 DSP 重定时器",
         "超高速 DSP SerDes 核心: 全数字 DSP 引擎",
         "  多阶自适应 FFE/DFE 均衡, 应对 64 GT/s 极高波特率",
         "Smart Gearbox: 硬件级协议转换引擎",
         "  PCIe 6.x Flit-mode ↔ Non-Flit-mode 无缝翻译",
         "遥测与诊断微控制器: 挂载 COSMOS 软件体系",
         "  内置 LTSSM 记录器 + 非破坏性硬件眼图扫描 (RX Margining)",
         "业界首家量产 PCIe 6.0 Retimer (2024)"],
        ["信号延伸: 在极高损耗信道下传输距离提升高达 3 倍",
         "利旧降本: 老旧 CPU/主板无缝对接最新一代高速加速器",
         "链路预算: ~36 dB (被澜起 43 dB 反超)",
         "自研 DSP: 核心 PHY 层技术自主可控",
         "Aries Smart Cable: Retimer 集成到 cable paddle card",
         "  支持直连 + 扇出电缆, PCIe 5.0 最远 7m, 6.x 最远 6m",
         "自动方向检测 + 极性校正 + Lane Reversal",
         "热插拔 + 不停机固件升级 + COSMOS 遥测"],
        accent=COLOR_GREEN)
    # 图片: 澜起 M88RT61632 框图 (竞争对手参考)
    img(prs.slides[-1], "M88RT61632_Block_Diagram.jpg", Inches(0.5), Inches(5.5), w=Inches(5.0))

    make_prod(prs, "Aries Smart Cable Module — 核心规格",
        specs=[
            ("协议", "PCIe 5.0 / 6.x / CXL 2.0 / 3.x"),
            ("速率", "64/32/8/5/2.5 GT/s, 自动链路均衡"),
            ("PCIe 5.0 距离", "最远 7 米, 多种铜缆规格"),
            ("PCIe 6.x 距离", "最远 6 米, 细径铜缆"),
            ("分叉模式", "1×16, 2×8, 4×4, 8×2 灵活配置"),
            ("高级特性", "自动方向检测 + 极性校正 + Lane Reversal + 热插拔"),
            ("诊断", "接收端 Lane Margining (时序+电压), PRBS 生成/检查"),
            ("固件", "不停机固件升级 (Non-disruptive FW Update)"),
        ],
        highlights=[
            "PCIe 6.0 业界首家量产",
            "7m 铜缆突破传统 DAC 距离极限",
            "COSMOS 遥测: 实时监控眼图张开度",
            "灵活分叉 + 自动均衡 + 即插即用",
        ],
        accent=COLOR_GREEN)
    # 图片: Aries Smart Cable Module 产品图
    img(prs.slides[-1], "aries_scm.png", Inches(8.8), Inches(5.0), w=Inches(3.8))

    make_table(prs,
        "Aries 竞争产品对比",
        ["指标", "Astera Aries (PCIe 6)", "澜起 M88RT61632", "谱瑞 PS8926", "Credo BlueHeron 224G"],
        [
            ["速率", "64 GT/s PAM4", "64 GT/s PAM4", "32 GT/s (PCIe 5.0)", "224 Gbps/通道"],
            ["通道数", "16", "16", "16", "多协议"],
            ["链路预算", "~36 dB", "高达 43 dB", "~36 dB", "40+ dB"],
            ["协议", "PCIe 6.x / CXL 3.x", "PCIe 6.x / CXL 3.x", "PCIe 5.0 / CXL 2.0", "UALink/ESUN/Ethernet"],
            ["SerDes", "自研 DSP", "自研 PAM4 IP", "自研", "自研 3nm DSP"],
            ["送样时间", "2024 (业界首家)", "2025.01", "已量产", "2026.01 送样"],
            ["软件生态", "COSMOS 遥测套件", "GUI + SDK", "基础工具", "PILOT 链路预测"],
            ["制程", "—", "—", "—", "3nm"],
        ],
        caption="📌 关键差距: Astera 先发 ~10个月 + COSMOS 软件生态是最大护城河; 澜起链路预算 43 dB 反超; Credo 3nm 224G 多协议是未来最强对手",
        small_fs=True)

    # ====== Part 4: Leo ======
    make_div(prs, "Leo — CXL 智能内存控制器", 4)

    make_prod_dual(prs,
        "Leo CXL Smart Memory Controller — 产品定义与技术架构",
        ["CXL 智能内存控制器芯片 (CXL Smart Memory Controller)",
         "",
         "低延迟数据路径中枢:",
         "  前端: 最高 x16 CXL/PCIe 接口控制器",
         "  后端: 2 通道 DDR5 最高 5600 MT/s",
         "  打通计算与存储的高速直连",
         "",
         "分层池化引擎 (P-Series):",
         "  硬件级动态寻址, 支持跨节点分配内存资源",
         "",
         "高级 RAS 微控制器:",
         "  独立纠错单元 + RDIMM 级故障隔离"],
        ["E-Series (内存扩展):",
         "  • 打破「内存墙」— 单节点内存容量直接翻倍",
         "  • 最高可扩展 2TB",
         "  • 解耦 CPU/GPU 与内存条的强绑定关系",
         "",
         "P-Series (内存池化):",
         "  • 消除 Stranded Memory (闲置内存孤岛)",
         "  • 按需划出, 用完收回",
         "  • 大幅降低 TCO",
         "",
         "降本增效: 昂贵 HBM 专注高算力,",
         "  大容量需求转移到便宜 DDR5 内存池",
         "",],
        accent=COLOR_ORANGE)
    # 图片: CXL 内存池化架构
    img(prs.slides[-1], "CXL_Application_CN.jpg", Inches(8.8), Inches(3.2), w=Inches(4.0))

    make_two(prs,
        "Leo 竞争产品对比 — CXL 内存控制器赛道",
        "🏆 Astera Leo",
        ["CXL 1.1 Smart Memory Controller",
         "E-Series: 单节点 2TB 内存扩展",
         "P-Series: 跨节点内存池化",
         "集成 DDR5 控制器 + RAS 微控制器",
         "CXL Retimer (Aries) + Leo 组合 = 全栈 CXL 方案",
         "COSMOS 统一遥测管理",
         "最大优势: 「Retimer + CXL Ctrl + 软件」全栈"],
        "⚔️ 竞争对手",
        ["澜起 M88MX6852: CXL 3.2 MXC, DDR5-8000",
         "  内置 RISC-V 处理器, 部分节点全球领跑",
         "  1211-ball FCBGA, 2025 年底送样",
         "Samsung CMM-D: CXL 内存模块 + E3.S 热插拔",
         "SK Hynix: CXL 内存模块 + 自研 CXL 控制器",
         "Marvell Structera X: CXL 2.0 + Arm Neoverse V2",
         "  X2404: 12 条 DIMM; X2504: DDR5 6400",
         "  + 内联 LZ4 压缩 + AES-XTS 256 加密",
         "UnifabriX: CXL 3.0 Smart Memory Node (2U)"],
        ra=True)
    # 图片: 澜起 CXL 应用案例 + Marvell 架构
    img(prs.slides[-1], "montage_cases.png", Inches(0.3), Inches(5.3), w=Inches(5.8))
    img(prs.slides[-1], "Marvell_arch.png", Inches(6.6), Inches(5.3), w=Inches(6.2))

    make_text(prs, "CXL 内存池化 — 业界全景",
        bullets=[
            "##机架内 (铜) — 已量产商用",
            "Astera Leo + Aries: AEC 线缆 + E3.S 内存扩展模块, Retimer CDR 恢复 PAM4",
            "Samsung/SK Hynix: E3.S 热插拔 + CXL 控制器 + DDR5, CXL Flit 直接译为 DDR5 RAS/CAS",
            "##系统级池化 — 展示动态切分",
            "UnifabriX: 2U CXL 3.0 Smart Memory Node + Switch 硬件路由 + Fabric Manager 秒级动态分配",
            "##跨机柜 (光) — 终局形态",
            "Ayar Labs TeraPHY: 硅光 Chiplet 与 CPU/Switch 同基板封装 → 单模光纤跨 50m",
            "阿里云 磐久 CXL + LPO: LPO 去 DSP 光模块, CXL 时钟直接驱动光器件, 省 DSP 延迟 ~数十 ns",
            "##CXL.mem vs RDMA 本质差异",
            "CXL.mem: Load/Store 内存语义, 64B 缓存行硬件直飞, 延迟 100~300 ns",
            "RDMA: 消息传递语义, 多级拷贝 + 协议栈, 延迟 1~5 μs",
            "CXL 将总线拓扑拉伸到数据中心规模 — 硬件状态机直飞, 零网卡, 零拆包",
        ])
    # 图片: CXL 内存池化架构图
    img(prs.slides[-1], "cxl_memory_pooling_architecture.png", Inches(0.5), Inches(5.5), w=Inches(5.5))

    # ====== Part 5: Scorpio ======
    make_div(prs, "Scorpio — 智能 Fabric 交换芯片", 5)

    make_prod_dual(prs,
        "Scorpio Smart Fabric Switch — 产品定义与技术架构",
        ["P-Series (PCIe 6 Fabric Switch):",
         "  • PCIe/CXL 混合流量调度",
         "  • 32-320 Lanes 灵活配置",
         "  • 全矩阵 Crossbar, 无阻塞交换",
         "",
         "X-Series (Memory Semantic Fabric):",
         "  • GPU Scale-Up 专用 Fabric",
         "  • 专攻大规模同构 GPU 后端连接",
         "",
         "Hypercast™ 网络内计算引擎:",
         "  • 芯片内部硬件数据复制与聚合模块",
         "  • 直接在交换层进行简单算术逻辑运算",
         "",
         "超宽 Crossbar: 端到端线速直通"],
        ["极低延迟单跳互联:",
         "  • AI 集群在一个拓扑层级内完成点对点通信",
         "  • 消除多级路由带来的延迟瓶颈",
         "",
         "算力卸载 (Hypercast™):",
         "  • 硬件引擎接管 AllGather/AllReduce",
         "  • 释放 GPU 算力用于纯粹模型训练",
         "",
         "填补 Broadcom/Microchip 之间的空白",
         "",
         "业界最高 Lane 数: 320 Lanes"],
        accent=COLOR_RED)
    # 图片: 芯动交换芯片 + XConn 框图
    img(prs.slides[-1], "Innosilicon_new1.jpg", Inches(0.5), Inches(5.0), w=Inches(5.5))
    img(prs.slides[-1], "xconn_km_diagram.png", Inches(6.5), Inches(5.0), w=Inches(6.2))

    make_table(prs,
        "Scorpio 竞争产品对比",
        ["指标", "Astera Scorpio", "Broadcom PEX", "芯动 GX9120", "Microchip Switchtec", "XConn XC50256"],
        [
            ["Lane 数", "32-320", "104 / 144", "120", "多种配置", "256"],
            ["协议", "PCIe 6 + CXL", "PCIe Gen5", "PCIe Gen5", "PCIe Gen5", "CXL 2.0 / PCIe 5.0"],
            ["延迟", "超低延迟", "—", "115 ns", "—", "业内最低"],
            ["特色", "Hypercast™ In-Network Compute", "成熟生态", "PUF + 防火墙, 16 GPU", "长期积累", "CXL Fabric Manager + MLD"],
            ["定位", "AI Fabric 专用", "通用 PCIe 交换", "国产破局者", "性价比", "CXL/PCIe 双模"],
            ["量产", "已量产 P 系列", "已量产多年", "2026.02 发布", "已量产", "已量产"],
        ],
        caption="📌 Astera Scorpio 的核心差异化: Hypercast™ 网络内计算 (卸载 AllReduce) + Memory Semantic Fabric (直指 GPU Scale-Up)",
        small_fs=True)

    make_text(prs, "PCIe Switch 市场格局：从垄断到国产突围",
        bullets=[
            "##国际格局",
            "Broadcom (博通) + Microchip (微芯) 长期垄断中高端",
            "Broadcom 在 AI 服务器占据绝对主导",
            "Astera Labs Scorpio 系列在 PCIe/CXL 交换 + Retimer 全球领先",
            "##国产破局 (2025-2026 落地元年)",
            "芯动科技 GX9120: 120 通道 PCIe Gen5, 115ns 延迟, 16 卡全互联 (2026.02 武汉发布)",
            "数渡科技: 104 通道 PCIe 5.0 Switch, 深度绑定华为昇腾 (910B/950), 万通发展控股",
            "井芯微电子 JXW8848: 全国产自主 Switch, 2025H2 量产",
            "澜起科技: Retimer + PCIe Switch 研发中",
            "##三大核心应用场景",
            "GPU 高速互联: CPU/GPU/NIC/NVMe 间动态调度, 支持 All-Reduce 参数同步",
            "资源池化 (CDI): 物理分区/虚拟化灵活分配 GPU/存储",
            "对等通信 (NTB): GPU Direct, 绕过 CPU 直接读写",
        ])
    # 图片: 芯动 16卡全互联
    img(prs.slides[-1], "Innosilicon_screenshot.png", Inches(7.5), Inches(5.3), w=Inches(5.0))

    # ====== Part 6: Taurus ======
    make_div(prs, "Taurus — 以太网智能线缆模块", 6)

    make_prod_dual(prs,
        "Taurus Ethernet Smart Cable Module — 产品定义与技术架构",
        ["以太网有源铜缆模块 (ACC), 面向 Scale-Out",
         "集成于 QSFP-DD / QSFP-DD800 / OSFP 标准接口",
         "支持 200G / 400G / 800G 三代速率",
         "",
         "以太网定制 DSP SerDes 核心:",
         "  • 专为 200/400/800GbE 复杂以太网环境优化",
         "  • 补偿 100G/Lane PAM4 铜线缆高插入损耗",
         "",
         "聚合/解聚合模块 (MAC/PHY 联合):",
         "  • 硬件级多通道速率拆分与组合",
         "",
         "穿透式直通数据路径:",
         "  • 仅做物理层信号调理, 不抓包"],
        ["超低延迟: 端到端 < 100 ns",
         "  (数据中心网络关键指标)",
         "",
         "智能速率匹配:",
         "  • 两端不对等速率即插即连",
         "  • 例: 200G 网卡 ↔ 400G 交换机端口",
         "",
         "功耗比 AOC 低高达 50%",
         "",
         "深度线缆诊断 + 安全固件加载",
         "不停机固件升级 (最高 1 MHz I²C)",
         "符合 CMIS 通用管理接口规范",
         "PTP 精密时钟协议 fanout 缓冲"],
        accent=COLOR_GOLD)
    # 图片: Taurus 产品图 + Credo AEC
    img(prs.slides[-1], "taurus.png", Inches(0.5), Inches(5.0), w=Inches(5.5))
    img(prs.slides[-1], "Credo_AEC.png", Inches(6.5), Inches(5.0), w=Inches(6.2))

    make_table(prs,
        "Taurus 产品矩阵 (按速率)",
        ["总速率", "料号", "封装", "线速率", "距离/线规"],
        [
            ["200G", "EM200-QDX-A", "QSFP-DD", "25G 或 50G/Lane", "3m 34AWG / 3m 32AWG"],
            ["400G", "EM400-QDX-A", "QSFP-DD", "50G 或 100G/Lane", "3m 32AWG / 3m 30AWG"],
            ["400G", "EM400-EPS-A", "OSFP", "50G 或 100G/Lane", "3m 32AWG / 3m 30AWG"],
            ["800G", "EM800-QDX-A", "QSFP-DD", "100G/Lane", "3m 30AWG"],
            ["800G", "EM800-EPS-A", "OSFP", "100G/Lane", "3m 30AWG"],
        ],
        caption="应用场景: ToR Switch ↔ Server NIC / Leaf Switch / Breakout → 多 Server NIC")

    make_table(prs,
        "Taurus 竞争产品对比 — AEC 赛道",
        ["指标", "Astera Taurus", "Credo ZeroFlap AEC", "澜起 PCIe 6 AEC", "Marvell/Broadcom DSP"],
        [
            ["协议", "Ethernet (Scale-Out)", "PCIe + Ethernet", "PCIe 6.x / CXL 3.x", "Ethernet DSP"],
            ["最高速率", "800G", "1.6T", "PCIe 6.0 x16", "800G+ DSP"],
            ["延迟", "< 100 ns", "超低延迟", "—", "—"],
            ["距离", "3m (30-34 AWG)", "7m (含 PCIe)", "机箱内外多场景", "—"],
            ["特色", "PTP + 速率匹配", "市占率 ~88%", "国内率先推出", "集成于安费诺/莫仕接头"],
            ["量产状态", "已量产", "已量产+PCIe 6 送样", "2026.01 发布", "已量产"],
            ["软件", "COSMOS 遥测", "PILOT 链路预测", "GUI + SDK", "OEM 集成"],
        ],
        caption="📌 关键格局: AEC 市场 Credo 以 ~88% 市占率主导, Astera 从 PCIe Aries 扩展到 Ethernet Taurus 实现双协议覆盖, 澜起从 Retimer 芯片切入 AEC 线缆实现垂直整合",
        small_fs=True)
    # 图片: Credo ZeroFlap Optics + BlueHeron
    img(prs.slides[-1], "Credo_ZeroFlap_Optics.png", Inches(0.3), Inches(5.0), w=Inches(6.0))
    img(prs.slides[-1], "Credo_BlueHeron.jpg", Inches(6.8), Inches(5.0), w=Inches(6.0))

    # ====== Part 7: COSMOS ======
    make_div(prs, "COSMOS 软件平台与生态壁垒", 7)

    make_text(prs, "COSMOS — 软件粘合剂",
        bullets=[
            "##COSMOS 是什么",
            "Astera Labs 的统一遥测与管理软件平台",
            "将所有硬件产品 (Aries/Scorpio/Leo/Taurus) 统一到单一管理界面",
            "实时监控眼图张开度、均衡器水平、结温等关键指标",
            "可配置中断告警 + Full C/Python SDK",
            "##COSMOS 的商业价值",
            "不是卖软件, 而是用软件绑定硬件 — 提高客户迁移成本",
            "让运维团队能够管理数万条链路",
            "加速故障隔离与诊断 → 降低数据中心停机时间",
            "##为什么 COSMOS 是真正的护城河",
            "硬件规格可以追赶, 但运维软件 + 海量部署验证需要时间积累",
            "澜起有 GUI + SDK, Credo 有 PILOT, 但 COSMOS 的跨产品线统一性是独有优势",
            "云厂商深度集成: NVIDIA/AWS/Meta 已经将 COSMOS 嵌入运维流程",
        ],
        alert="COSMOS 是 Astera 最被低估的资产 — 软件生态的迁移成本远高于芯片替换成本")

    make_two(prs,
        "Astera Labs 全栈竞争壁垒",
        "🔧 硬件壁垒",
        ["SerDes/DSP IP: 自研核心 PHY 层技术",
         "  Aries 系列基础, PAM4/224G 演进路线清晰",
         "Switching Fabric IP: Scorpio 核心",
         "  320 Lanes Crossbar + Hypercast™",
         "CXL Protocol IP: Leo 核心",
         "  国内极少数掌握该层级技术的厂商",
         "先发优势: PCIe 6 Retimer 领先 ~10个月",
         "全栈整合: 单一供应商同时提供 Retimer + Switch + Memory Ctrl + Cable"],
        "🌐 软件与生态壁垒",
        ["COSMOS 遥测套件: 跨产品线统一管理平台",
         "  Full C/Python SDK + 实时链路诊断",
         "客户绑定: 已深度集成 NVIDIA/AWS/Meta",
         "互操作性认证矩阵: CPU/GPU/SSD/NIC 全覆盖",
         "超大规模验证: 万卡集群极限工况考验",
         "不停机固件升级: 所有产品线均支持",
         "产业链位置: 「中立连接供应商」",
         "  不与客户 (NVIDIA/AMD/Intel) 直接竞争"],
        ra=True)

    # ====== Part 8: 竞争格局总结 ======
    make_div(prs, "竞争格局总结", 8)

    make_table(prs,
        "全栈竞争矩阵 (2026)",
        ["公司", "Retimer", "PCIe Switch", "CXL Ctrl", "AEC", "软件平台"],
        [
            ["Astera Labs ★", "★★★", "★★★", "★★", "★★", "★★★"],
            ["Broadcom", "★★", "★★★", "—", "★", "—"],
            ["NVIDIA", "自用", "NVSwitch(私有)", "间接", "—", "自用"],
            ["Credo", "★★★", "—", "—", "★★★", "★"],
            ["Marvell", "★", "定制ASIC", "★", "★", "—"],
            ["Microchip", "—", "★★", "—", "—", "—"],
            ["澜起科技", "★★★", "研发中", "★★★", "★★", "★"],
            ["Samsung/SK", "—", "—", "★★★", "—", "—"],
        ],
        caption="★ 数量表示竞争力强度 | 只有 Astera Labs 覆盖全部 4 条硬件产品线 + 软件平台 — 全栈策略是核心优势, 但也意味着同时与多家公司竞争")

    make_table(prs,
        "关键差异化维度对比",
        ["维度", "Astera Labs", "Broadcom", "Credo", "澜起科技", "NVIDIA"],
        [
            ["商业模式", "Fabless 连接芯片", "多元化半导体", "Fabless 连接芯片", "Fabless 内存接口", "垂直整合"],
            ["核心产品", "Retimer+Switch+CXL+AEC", "Switch+Retimer", "AEC+Retimer+DSP", "Retimer+CXL+AEC", "GPU+NVSwitch"],
            ["协议阵营", "开放标准 (PCIe/CXL)", "开放+私有", "开放+私有", "开放标准", "私有 (NVLink)"],
            ["软件生态", "COSMOS ★★★", "基础工具", "PILOT ★", "GUI+SDK ★", "CUDA ★★★"],
            ["AI 定位", "连接层供应商", "通用交换机", "SerDes IP 供应商", "内存互连+高速运力", "全栈 AI 平台"],
            ["FY2025 收入", "$852.5M (+93%)", "—", "$437M", "¥54.56亿 (+50%)", "—"],
            ["中国市场", "未直接进入", "已进入", "有限", "主场", "受限"],
        ],
        small_fs=True)

    make_text(prs, "「Switzerland of Connectivity」定位分析",
        bullets=[
            "##中立定位的前提条件",
            "GPU 市场不是 NVIDIA 垄断 (需要 AMD/Intel/自研 ASIC 替代品) — 当前 NVIDIA >80%",
            "Hyperscaler 维持多 vendor 策略 — 确实在推 (Google TPU, Amazon Trainium, MS Maia)",
            "PCIe/CXL 持续演进 — 利好",
            "NVIDIA 不开放 NVLink — 利好",
            "##核心矛盾",
            "NVIDIA 越封闭 → Astera 越有价值 (开放标准替代方案)",
            "但 Astera 短期最大客户是 NVIDIA GPU 集群中的连接需求",
            "(因为 NVIDIA GPU 也需要 PCIe retimer/switch 来连接 NIC/NVMe 等非 NVLink 设备)",
            "##风险",
            "NVIDIA 完全开放 NVLink 或收购一家连接公司 → 中立定位失效",
            "Marvell 2026 年收购 XConn ($5.4亿) + Celestial AI ($32.5亿) → 竞争加剧",
        ],
        alert="Marvell 两笔重大收购合计 ~$38亿, 正在从「部分竞争」升级为「全面竞争」")

    # ━━━━ 总结 ━━━━
    make_text(prs, "总结与展望",
        bullets=[
            "##核心结论",
            "Astera Labs 是 AI Infra 连接层最全面的供应商 — 覆盖 Retimer + Switch + CXL Ctrl + AEC + 软件",
            "COSMOS 软件平台是最被低估的护城河 — 硬件可以追赶, 软件生态 + 客户集成需要数年积累",
            "以开放标准 (PCIe/CXL) 对抗私有协议 (NVLink), 「中立定位」是核心战略资产",
            "##竞争态势",
            "Retimer: 澜起 (43 dB 链路预算反超) + Credo (3nm 224G 多协议) 是最大威胁",
            "CXL Memory: 澜起 MXC (CXL 3.2) 部分节点全球领跑",
            "Switch: 芯动 GX9120 破局, Broadcom 仍是最大对手",
            "AEC: Credo 以 ~88% 市占率主导",
            "Marvell 收购 XConn + Celestial AI 正在重塑竞争格局",
            "##值得关注的趋势",
            "CXL 内存池化从概念走向量产 (Samsung/SK Hynix/澜起均已送样)",
            "PCIe 7.0 (128 GT/s) 与 224G SerDes 演进将重塑 Retimer 市场",
            "硅光/CPO 从终局走向现实 (Ayar Labs $37.5亿估值, Celestial AI $32.5亿被收购)",
        ])

    # ━━━━ 致谢 ━━━━
    make_end(prs, "葛良晨")

    # ━━━━ 保存 ━━━━
    prs.save(output_path)
    sz = Path(output_path).stat().st_size
    print(f"✅ Astera Labs 调研 PPTX 已生成: {output_path} ({sz/1024:.0f} KB)")
    print(f"   共 {len(prs.slides)} 页幻灯片")

def main():
    p = argparse.ArgumentParser(description="Astera Labs 全面调研 PPTX 生成脚本")
    p.add_argument("-o", "--output", default="asteralabs_research.pptx",
                   help="输出 .pptx 路径 (默认: asteralabs_research.pptx)")
    args = p.parse_args()
    build(args.output)

if __name__ == "__main__":
    main()
