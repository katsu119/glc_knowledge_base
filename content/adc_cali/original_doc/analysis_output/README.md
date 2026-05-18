# ADC校准参考文档 - 分析输出目录

## 目录结构

```
analysis_output/
│
├── README.md                          ← 本文件：目录说明
├── pdf_processing_pipeline.py         ← PDF处理流水线脚本
├── TIADC校准技术深度分析报告.md        ← 综合深度分析报告
│
├── extracted_text/                    ← PDF提取的文本文件
│   ├── gain_loop_text.txt
│   ├── offset__ loop_text.txt
│   └── time_skew__ (13)_text.txt
│
├── extracted_images/                  ← PDF转换的图片文件
│   ├── gain_loop_images/
│   ├── offset__ loop_images/
│   └── time_skew__ (13)_images/
│
└── pdf_processing_report.json         ← PDF处理汇总报告
```

## 文件说明

### 1. `pdf_processing_pipeline.py`
PDF处理自动化脚本。使用PyMuPDF库提取文本、转换图片、生成元数据报告。
```bash
python pdf_processing_pipeline.py
```

### 2. `TIADC校准技术深度分析报告.md`
核心分析报告，约800行，涵盖：
- TIADC基本原理与失配分析
- 三种校准算法（Offset/Gain/Timing Skew）的数学原理
- MATLAB代码与PDF文档的逐项对照分析
- 综合校准流水线详解
- ADC行为模型（二进制/非二进制）原理解析
- 性能评估体系（SNR/SINAD/SFDR/ENOB）

### 3. `pdf_processing_report.json`
PDF处理的结构化元数据，包含文件大小、页数、提取状态等。

## 数据来源

- **PDF文档**: 3份（gain_loop.pdf, offset__ loop.pdf, time_skew__ (13).pdf）
- **MATLAB代码**: ADCCali_64Gnew/ 目录下的10+个 .m 文件
- **汇总文档**: ADCCali_64Gnew/ADC校准技术汇总文档.md
