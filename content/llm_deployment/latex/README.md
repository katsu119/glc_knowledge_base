LaTeX 子项目：用于在公司内网进行 LLM 部署研究记录与演示。

包含：
- `notes.tex`：研究与资源安排的文档（XeLaTeX，支持中文）。
- `presentation.tex`：Beamer 演示模板（XeLaTeX + xeCJK）。
- `Makefile`：构建 PDF 的便捷命令。

构建：

```bash
cd content/llm_deployment/latex
make all
```
