# Git 工作流规范指南

本文档旨在介绍业界通用的 Git 工作流，并为本项目提供版本控制建议。选择合适的工作流可以提高团队协作效率，确保代码质量和发布流程的稳定性。

> **提示**：本文档同时包含了传统命令（如 `checkout`）和现代推荐命令（如 `switch`, `restore`）。

---

## 1. Git Flow (经典工作流)

适用于有固定发布周期的项目。

### 核心分支
- **master (main)**: 始终保持可生产状态的代码。
- **develop**: 开发主分支，包含下一个版本的最新交付代码。

### 常用指令
```bash
# 1. 初始化: 从 master 创建并切换到 develop 分支
git checkout -b develop master
# [新命令] git switch -c develop master

# 2. 开发新功能 (Feature): 从 develop 切出功能分支
git checkout -b feature/my-feature develop
# [新命令] git switch -c feature/my-feature develop

# ... 进行开发提交 ...

# 完成后合并回 develop
git checkout develop            # 或 git switch develop
git merge --no-ff feature/my-feature
git branch -d feature/my-feature

# 3. 发布版本 (Release): 从 develop 切出发布分支
git checkout -b release/v1.0.0 develop
# [新命令] git switch -c release/v1.0.0 develop

# ... 进行必要的修复 ...

# 合并回 master 并打上标签
git checkout master             # 或 git switch master
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0"
# 同时合并回 develop
git checkout develop            # 或 git switch develop
git merge --no-ff release/v1.0.0
git branch -d release/v1.0.0

# 4. 紧急修复 (Hotfix): 直接从 master 切出
git checkout -b hotfix/fix-bug master
# [新命令] git switch -c hotfix/fix-bug master

# ... 快速修复 ...

git checkout master             # 或 git switch master
git merge --no-ff hotfix/fix-bug
git tag -a v1.0.1 -m "Fix bug v1.0.1"
git checkout develop            # 或 git switch develop
git merge --no-ff hotfix/fix-bug
git branch -d hotfix/fix-bug
```

---

## 2. GitHub Flow (轻量级工作流)

适合持续交付（CD）和快速迭代的项目。

### 基本流程与指令
```bash
# 1. 切出具有描述性的分支
git checkout master             # 或 git switch master
git pull origin master
git checkout -b feature-description
# [新命令] git switch -c feature-description

# 2. 提交更新
git add .
git commit -m "Add some feature"

# 3. 推送分支
git push origin feature-description

# 4. 合并回 master (本地操作示例)
git checkout master             # 或 git switch master
git merge feature-description
git push origin master
git branch -d feature-description
```

---

## 3. GitLab Flow (结合环境的工作流)

引入了“环境分支”的概念，适用于需要区分预发和生产环境的项目。

### 常用指令
```bash
# 1. 开发阶段在 master
git checkout master             # 或 git switch master

# 2. 发布到预生产环境
git checkout pre-production     # 或 git switch pre-production
git merge master
git push origin pre-production

# 3. 发布到生产环境
git checkout production         # 或 git switch production
git merge pre-production
git push origin production
```

---

## 4. Trunk-Based Development (基于主干的开发)

高频拉取与合并，适合自动化程度极高的团队。

### 核心操作
```bash
# 1. 切换到主干
git checkout master             # 或 git switch master

# 2. 线性拉取
git pull --rebase origin master

# 3. 推送小额改动
git add .
git commit -m "Small incremental change"
git push origin master
```

---

## 5. 撤销与回滚 (Rollback & Revert)

在开发过程中难免出错，Git 提供了多种方式来撤销更改。

### 常用撤销指令
```bash
# --- 场景 1: 撤销工作区还未 add 的修改 ---
# 传统命令:
git checkout -- <file_name>
git checkout .
# [现代推荐命令]:
git restore <file_name>         # 恢复单个文件
git restore .                  # 恢复所有文件

# --- 场景 2: 撤销已经 add 但还未 commit 的修改 ---
# 传统命令:
git reset HEAD <file_name>
# [现代推荐命令]:
git restore --staged <file_name>

# --- 场景 3: 撤销已经 commit 但还未 push 的修改 ---
# 回退并保留改动 (Soft Reset)
git reset --soft HEAD~1
# 回退并彻底丢弃改动 (Hard Reset)
git reset --hard HEAD~1

# --- 场景 4: 撤销已经 push 的修改 ---
# 安全回滚: 生成反向提交，不破坏历史记录
git revert <commit_id>
git push origin <branch_name>

# --- 场景 5: 临时保存进度 ---
git stash                       # 压入堆栈
git stash list                  # 查看列表
git stash pop                   # 弹出最近进度
git stash apply stash@{0}       # 应用特定进度
```

---

## 6. LaTeX 项目实战教程 (GitHub Flow 简易版)

针对当前的 LaTeX 项目结构，指导你如何进行日常维护。

### 常见场景实操

#### 场景 A：添加一个新章节（如 `content/new_chapter.tex`）
1.  **新建分支**：`git switch -c add-new-chapter`
2.  **创建并编辑文件**：在 `content/` 下创建新文件，在 `main.tex` 中 `\include`。
3.  **提交代码**：
    ```bash
    git add content/new_chapter.tex main.tex
    git commit -m "feat: 增加新章节 Xxx"
    ```
4.  **合并回主干**：`git switch master` -> `git merge add-new-chapter`。

#### 场景 B：更新插图（更新 `figures/` 下的 PDF/PNG）
1.  **覆盖文件**：直接将新的图片文件放入 `figures/` 文件夹。
2.  **提交**：`git add figures/` -> `git commit -m "style: 更新系统架构图"`。

#### 异常处理：编译中间文件冲突
如果你不小心追踪了 `.aux` 或 `.log` 文件：
```bash
# 从 Git 追踪中移除这些文件（但保留本地文件）
git rm --cached *.aux *.log *.pdf
git commit -m "build: 移除误追踪的中间文件"
```

---

## 7. LaTeX 项目深度实战：Git Flow 完整生命周期

本章节模拟一个完整的 LaTeX 文档开发周期，详细解释每一步操作及参数含义。

### 第一阶段：初始化开发环境
在项目开始时，我们需要建立“开发主线”。

```bash
# 传统命令：git checkout -b develop master
# 现代命令：git switch -c develop master
# 参数解释：
#   switch: 专门用于切换分支的命令（Git 2.23+ 引入，语义更明确）。
#   -c (或 --create): “创建”参数。
#   整个命令含义：基于 master 分支，创建一个名为 develop 的新分支并立即切换过去。
```

### 第二阶段：开发新章节 (Feature)
```bash
# 1. 创建功能分支
git checkout -b feature/history-chapter develop
# 或者使用现代命令：git switch -c feature/history-chapter develop

# 2. 编写代码并提交
git add content/history.tex main.tex
git commit -m "feat: 完成历史背景章节初稿"

# 3. 合并回开发分支 (使用 --no-ff)
git checkout develop            # 或 git switch develop
# 参数解释：--no-ff (no-fast-forward) 强制生成合并提交，保留分支历史痕迹
git merge --no-ff feature/history-chapter

# 4. 清理
git branch -d feature/history-chapter
```

### 第三阶段：准备发布版本 (Release)
```bash
# 1. 创建发布分支
git checkout -b release/v1.0.0 develop

# 2. 进行微调并提交
git commit -am "chore: 更新版本号为 v1.0.0"

# 3. 正式发布：合并到 master 并打标签
git checkout master
git merge --no-ff release/v1.0.0
# 参数解释：-a (附注标签)；-m 标签信息。这是版本归档的关键里程碑
git tag -a v1.0.0 -m "正式版 v1.0.0 发布"

# 4. 同步回开发分支并清理
git checkout develop
git merge --no-ff release/v1.0.0
git branch -d release/v1.0.0
```

### 第四阶段：紧急修复 (Hotfix)
```bash
# 1. 从 master 切出修复分支
git checkout -b hotfix/fix-error master

# 2. 修复 Bug 并提交
git commit -am "fix: 纠正史实错误"

# 3. 合并回 master 并更新补丁版本
git checkout master
git merge --no-ff hotfix/fix-error
git tag -a v1.0.1 -m "紧急修复补丁 v1.0.1"

# 4. 合并回 develop (防止 Bug 在未来版本复现)
git checkout develop
git merge --no-ff hotfix/fix-error
git branch -d hotfix/fix-error
```

---

## 总结与建议

| 指令 | 核心作用 | 关键参数 | 什么时候用 |
| :--- | :--- | :--- | :--- |
| `git checkout -b` | 另起炉灶 | `-b` (新建并切) | 开发新功能或准备发布前 |
| `git switch -c` | 另起炉灶(推荐) | `-c` (创建并切换) | 同上，语义更清晰 |
| `git merge --no-ff` | 隆重合并 | `--no-ff` (保留痕迹) | 合并独立成果到主线时 |
| `git tag -a` | 刻碑纪念 | `-a` (附注标签) | 每一个正式发布的版本节点 |
| `git restore` | 时光倒流 | `--staged` (从暂存区回退) | 撤销误操作时 |

**本项目建议**:
对于 LaTeX 项目，保持 **GitHub Flow** 是最佳实践。如果涉及大型书籍的多人协作，**Git Flow** 能提供更清晰的版本归档（Tags）。务必确保中间文件不进入仓库。
