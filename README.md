<div align="center">

# 学者问道 · Scholar-Wendao

> *问道于古今学者* · *Ask the way of scholars across time*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Inspired by Nuwa](https://img.shields.io/badge/Inspired%20by-%E5%A5%B3%E5%A8%B2.skill-orange)](https://github.com/alchaincyf/nuwa-skill)
[![v0.4.1](https://img.shields.io/badge/version-v0.4.1-blue)](#)

**为人文社科研究者建立的、由 agent 驱动的、端到端学术研究工作流系统。**

输入一个学者的名字 → 自动多语言多源采集 → PDF 证据提取 → 概念地图蒸馏 → 同时丰富用户的图书馆（PDF + Cards）/ 概念笔记 / 主题地图 → 生成可调用的"分析镜片"skill → 提交到 GitHub。

不是 AI 陪聊。不是角色扮演。**是研究者每天用的工作流。**

[**这是什么**](#这是什么) · [**三大产物**](#三大产物) · [**端到端工作流**](#端到端工作流) · [**配置规范**](#配置规范) · [**已有案例**](#已有案例) · [**诚实边界**](#诚实边界--humble-epistemics) · [English](README_EN.md)

</div>

---

## 这是什么

人文社科研究者面对一个学者的实际工作量包括四件事，过去是分散在四套工具里：

| 工作 | 传统工具 | 痛点 |
|---|---|---|
| 1. **资料搜集** | Google Scholar / Zotero / 手动下载 | OA 链接失败率 75%；闭源专著要个个找；非 book 资料（讲座/访谈/集体著作）无统一入口 |
| 2. **PDF 全文阅读** | Adobe / Preview | 17 部书逐本读概念抽取太慢 |
| 3. **思想分析** | 自己写读书笔记 | 重复写"X 的核心概念"段，跨学者难复用 |
| 4. **知识库整合** | Obsidian + 手工 wikilink | 蒸馏完成后再手工把材料归档到图书馆/笔记/MOC，常常拖延 |

**学者问道把这四件事合并成一个 agent 驱动的端到端流程。** 用户的角色降为：决策点确认 + 提供配置参数。

---

## 三大产物

每跑一次蒸馏，scholar-wendao **同时**生产三件成品：

### 🏛️ 1. Library 图书馆增长

把多源采集到的 PDF 落入用户既有的扁平命名 Library（如 `Library/_files/{Author}{Year}_{slug}.pdf`），并自动生成符合用户模板的 Library Card（`Library/Cards/{Author}{Year}.md`，含 frontmatter / APA 引用 / 多语言版本表 / 概念命中分布 / Top 引用片段）。

### 🔬 2. Perspective Skill

`examples/{slug}-perspective/SKILL.md`：当前学者的可调用分析镜片。包括：

- 3-7 个核心概念（每个含定义、与他人关系、局限、关键引文，引文必须 page-anchor 可证）
- 5-10 条方法论进路（碰到 X 类材料的分析步骤）
- 学术坐标 + 智识谱系（上游 / 横向 / 下游）
- 重大论战与立场转变
- 人格与处世（独立章节，BRACKETING 双层标注）
- 六大诚实边界（默会知识 / 化石化 / 公开-私下 / 传记修辞 / 漫画化 / 死亡-尊重）

### 🕸️ 3. Knowledge Base 联结

把蒸馏过程产出的素材**落入用户 Vault 的对应位置**，并在 MOC / 概念笔记 / 谱系笔记 / 人物志中追加 wikilink 索引：

- `Library 数字图书馆/Cards/` ← 17 个 Card
- `Concepts 概念与理论/{第三持存,药理学,...}.md` 末尾追加"📎 v0.4 PDF Evidence Anchors"
- `Permanent Notes 永久笔记/{斯蒂格勒与德里达,...}.md` 谱系笔记加 wikilink
- `MOC Maps 主题地图/{学者}研究 MOC.md` 加"🔬 v0.4 蒸馏素材库"段
- `People 人物志/{学者中文名}.md` 加 biography 链接
- `Projects 项目/学者问道/{学者} 蒸馏/` 完整工作区（research / biography / pdf_evidence / SKILL.md）

---

## 双工作流架构（v0.4.2）

> 本节面向 agent。scholar-wendao 显式分为**两个独立可触发的子工作流** + 共享数据层。每个 Workflow 可单独跑、可重复跑，组合形式由触发词决定。

### 触发词路由

| 用户输入意图 | Workflow | 路径 |
|---|---|---|
| "**搜集 X 的资料**" / "**为 X 建图书馆**" / `build-library X` | **A 单跑** | A.0 → A.5 |
| "**蒸馏 X**" / "**做 X 的分析镜片**" / `distill X` | **B 单跑** | B.1 → B.6 |
| "**学者问道 X**"（默认端到端） | **A → B** | 完整流程 |
| "**重蒸 X**" | **B 重做模式** | 旧 SKILL.md 进 archive |
| "**更新 X 的 skill**" | **B 轻量 update** | 增补不重写 |
| "**我有 PDF 想加到 X 的库**" / "intake PDF for X" | **A.4 单步** | `intake_manual_pdf.py` |

### Workflow A · 图书馆建设

| Phase | 内容 | 工具 |
|---|---|---|
| **A.0** | 配置（`_library_config.md`）+ Library 覆盖率扫描 | (config) |
| **A.1** | Metadata 全收集（"无漏" manifest） | `harvest_works.py` + 4 harvester(v0.4.3) |
| **A.2** | Tier 1+2 自动下载（OA / yt-dlp / scrape） | `download_open_access.sh` |
| **A.3** | Tier 3+4 manifest 输出（待手动 / 浏览器助手项） | `annas_acquire.py`（默认 manifest-only） |
| **A.4** | **用户主动导入** ← 一等公民入口 | `intake_manual_pdf.py` |
| **A.5** | 生成 / 增量更新 Library Cards | `generate_library_cards.py` |

### Workflow B · 学者蒸馏

| Phase | 内容 | 工具 |
|---|---|---|
| **B.1** | extract_pdf_evidence（基于 Library 当前状态） | `extract_pdf_evidence.py` |
| **B.2** | 7 agent 调研（research / biography） | spawn agents |
| **B.3** | 框架提炼（concepts / heuristics / genealogy / etc） | (LLM synthesis) |
| **B.4** | SKILL.md 构建 | (template fill) |
| **B.5** | 质量验证（含引文 page-anchor 核验） | `quality_check.py` |
| **B.6** | Vault 同步（回灌 wikilinks） | `sync_to_vault.py` |

### 4 层资料采集架构（acquisition_tier）

每条资料在 `_acquisition_manifest.json` 中标注 `acquisition_tier` + `priority`：

| Tier | 自动化程度 | 适用源 | 工具 |
|---|---|---|---|
| **1 · 完全 API** | 100% 自动 | OpenAlex / Crossref / Semantic Scholar / unpaywall | `harvest_works.py` |
| **2 · 友好 scrape** | 90% 自动 | YouTube / Vimeo / 学者主页 / 出版社 OA | `harvest_*.py`（4 个 v0.4.3） |
| **3 · 浏览器助手** | 50% 自动 | annas / paywall / Cairn 锁定文章 | 浏览器 cookies → 工具 |
| **4 · 完全手动** | 0% 自动，工具辅助归档 | annas 严格反爬 / 闭源专著 / 罕见档案 | `intake_manual_pdf.py` |

**核心设计原则**：scholar-wendao 不假设"全自动化采集"。**"无漏"原则的实操含义是 metadata 无漏，不是 PDF 全到手**。Tier 3+4 资料显式列入 manifest，让用户决策。

---

## 端到端工作流（命令清单）

> 本节面向 agent。每一 Phase 给出**具体命令**与**退出条件**。

### Phase 0：入口分流

agent 收到用户请求后，按 `SKILL.md` Phase 0 表格判定路径（直接 / 主题 / 诊断）。

### Phase 0.5：配置 + Library 覆盖率扫描

**1. 创建 `examples/{slug}-perspective/` 目录结构**

```bash
SLUG="stiegler"   # 学者标识
mkdir -p examples/${SLUG}-perspective/references/{research,biography}
mkdir -p examples/${SLUG}-perspective/_pdf_evidence
```

**2. 写 `_library_config.md`**

按 [`references/_library_config-template.md`](references/_library_config-template.md) 模板填 frontmatter（13 个字段，含 7 个 Vault 子路径），保存到：
`examples/${SLUG}-perspective/references/research/_library_config.md`

**3. 询问归档策略**

- `archive_layout`: `flat`（推荐）/ `by-language`
- `examples_retention`: `minimal` / `lightweight`（默认）/ `full`
- `vault_archive_path`: 用户 Vault 的"知识库"根

**4. 扫描覆盖率**

```bash
# Library 中已有该学者的 PDF 数 → 决定纯网络/本地补/本地优先/纯本地模式
COUNT=$(find "$LIBRARY_ROOT" -iname "${PREFIX}*.pdf" | wc -l)
```

写入 `_library_config.md` 的 `coverage_report.coverage_percent`。

### Phase 1.0：多源信息采集（v0.4.1 加 4 个新源）

```bash
# 学术 archive (OpenAlex / Crossref / Semantic Scholar / arXiv via Academix MCP)
python3 scripts/harvest_works.py "Bernard Stiegler" \
    -o examples/${SLUG}-perspective/references/research/07-archive

# OA 资源批量下载（v0.4 新增 unpaywall + HTML 落地页 fallback）
bash scripts/download_open_access.sh \
    examples/${SLUG}-perspective/references/research/07-archive.json \
    "${LIBRARY_FILES_DIR}" \
    flat \
    "${PREFIX}"

# v0.4.3 backlog: 4 个非 book harvester（"无漏"原则）—— 待写
# python3 scripts/harvest_lectures.py "Bernard Stiegler"        # YouTube/Vimeo
# python3 scripts/harvest_french_journals.py "Bernard Stiegler" # Cairn/OpenEdition
# python3 scripts/harvest_homepages.py "Bernard Stiegler"       # Semantic Scholar/PhilPapers
# python3 scripts/harvest_collectives.py "Bernard Stiegler"     # ARS Industrialis/Internation
```

### Phase A.3：Tier 3+4 acquisition manifest 输出（v0.4.2）

把 annas-archive 等反爬严格的源**仅生成 manifest 不实际下载**。manifest 写出待手动下载清单 + 获取建议。

```bash
# v0.4.2 默认即 manifest-only（不实际下载）
python3 scripts/annas_acquire.py \
    examples/${SLUG}-perspective/references/research/07-archive.json \
    -o examples/${SLUG}-perspective/references/research/ \
    --archive-layout flat \
    --prefix "${PREFIX}"
```

输出：
- `_acquisition_manifest.json`（机器可读，4 tier 标注 + priority）
- `_acquisition_manifest.md`（人类可读，按 priority 排序）

### Phase A.4：用户主动导入（v0.4.2 一等公民入口）

用户从浏览器手动下载 PDF 后，用本工具一行命令归档：

```bash
# 单部导入（fully spec）
python3 scripts/intake_manual_pdf.py \
    ~/Downloads/Bifurquer-Stiegler.pdf \
    --config examples/${SLUG}-perspective/references/research/_library_config.md \
    --year 2020 --slug Bifurquer --lang fr \
    --execute

# 关联 manifest 中已有条目
python3 scripts/intake_manual_pdf.py PDF \
    --config CONFIG \
    --manifest-id stiegler-2020-bifurquer-fr \
    --execute

# 批量（auto-infer year + lang from filenames）
python3 scripts/intake_manual_pdf.py \
    ~/Downloads/Stiegler*.pdf \
    --config CONFIG \
    --auto-infer \
    --execute
```

自动行为：
1. 重命名为 `{prefix}{year}_{slug}_{lang}.pdf`（按 `archive_layout`）
2. 移动（`--copy` 改为复制）到 Library/_files
3. 跑 `extract_pdf_evidence`（仅该新 PDF）
4. 跑 `generate_library_cards`（增量）→ Card
5. 在 `_acquisition_manifest.json` 标记 `intake_completed`

**Phase A.4 是可重复入口** —— 用户每天补一两本，scholar-wendao 累积式增长 Library。不需要重跑 Workflow A 全部。

### Phase 1.0.5：PDF Evidence 强制提取（v0.4 新增）

**触发条件**：本地优先 / 纯本地模式（覆盖率 ≥ 30%）。

```bash
python3 scripts/extract_pdf_evidence.py \
    --library "${LIBRARY_FILES_DIR}" \
    --filter "${PREFIX}*.pdf" \
    --concepts examples/${SLUG}-perspective/_pdf_evidence/_concepts.json \
    --out examples/${SLUG}-perspective/_pdf_evidence \
    --head 30 --tail 30
```

输出：每部 PDF → `_pdf_evidence/{book}.md`（head + tail + 概念锚点）+ `_index.json` + 自动检测 OCR backlog。

### Phase 1：7 个并行 Agent

按 `SKILL.md` Phase 1 表格 spawn 7 个 agent。**每个 agent 必须 `cat` 输出文件路径作为退出条件**（v0.4 P1 #3 修复）。

主流程在 Phase 1.5 用 `ls -la references/research/` 兜底验证 + 自写缺失文件。

### Phase 2.x：框架提炼

按 SKILL.md Phase 2.1-2.8 填充。**v0.4 强制**：每核心概念末尾"证据来源"小节链接 `_pdf_evidence/{book}.md`，引文必须 page-anchor 可证。

### Phase 2.9：Library Card 生成（v0.4.1 新增）

```bash
python3 scripts/generate_library_cards.py \
    --config examples/${SLUG}-perspective/references/research/_library_config.md \
    --evidence-dir examples/${SLUG}-perspective/_pdf_evidence \
    --archive-json examples/${SLUG}-perspective/references/research/07-archive.json
```

对每部 PDF 生成 / 增量更新 Library Card 写入 `{vault}/Library/Cards/{Author}{Year}.md`。已有 Card → 仅追加"📎 v0.4 PDF Evidence Anchors"段不破坏用户手写内容。

### Phase 3：SKILL.md 构建

按 `references/scholar-template.md` 填充组装。

### Phase 4：质量验证

```bash
python3 scripts/quality_check.py \
    --skill examples/${SLUG}-perspective/SKILL.md \
    --evidence-dir examples/${SLUG}-perspective/_pdf_evidence
```

**v0.4 8 项静态检查**（升级版）：

| 检查 | 阈值 |
|---|---|
| 6 大诚实边界声明 | 全部 |
| 概念地图 3-7 个 | hard limit |
| 方法论进路 ≥ 5 条 | hard limit |
| 调研时间标注 | regex bold-resilient |
| 默认分析镜片 + opt-in 对话 | 必须 |
| 一手来源占比 | ≥ 50% |
| **引文 page-anchor 核验** | ≥ 80% 可在 evidence 定位 |
| **Narrative-bracketing 双标注** | 形成性事件 100% |

不通过 → 标注薄弱环节 → 回到对应 Phase。

### Phase 5.5：Vault 同步（v0.4.1 新增）

```bash
python3 scripts/sync_to_vault.py \
    --config examples/${SLUG}-perspective/references/research/_library_config.md
```

把 `references/research/` + `references/biography/` + `_pdf_evidence/` + `SKILL.md` 复制到用户 Vault 的 `{project_workspace_path}/` 子目录。生成 `_vault_paths.md` 索引。

确认 Vault 内容无误后，可加 `--prune` 按 `examples_retention` 策略瘦身项目仓库（不可逆）。

**额外手工步骤**（v0.4.1 暂未自动化）：

- 6 概念笔记（Concepts/）末尾追加"📎 v0.4 PDF Evidence Anchors"
- 5 谱系笔记（Permanent Notes/）末尾追加 wikilink
- MOC 末尾追加"🔬 v0.4 蒸馏素材库"段
- 人物志末尾追加 biography wikilinks

stiegler 案例已实现（[examples/stiegler-perspective/](examples/stiegler-perspective/)）；这部分将在 v0.4.2 中合并到 `sync_to_vault.py --update-wikilinks`。

### Phase 6：GitHub 工作流

```bash
git add SKILL.md scripts/ references/ examples/${SLUG}-perspective/ README.md
git commit -F /tmp/commit_msg.txt   # commit 消息含 quality_check 得分 + Vault 路径概览
git push origin main
```

---

## 配置规范

### `_library_config.md` 模板

每个学者案例的配置文件，必须包含 v0.4.1 frontmatter（13 字段）：

```yaml
---
scholar_slug: "stiegler"
scholar_name: "贝尔纳·斯蒂格勒"
scholar_name_en: "Bernard Stiegler"
scholar_birth_year: 1952
scholar_death_year: 2020          # 已故 / null

archive_layout: "flat"            # flat | by-language
file_prefix: "Stiegler"

# Vault 路径（v0.4.1 必填）
vault_archive_path: "$HOME/.../02 · Knowledge"
library_files_path: "Library 数字图书馆/_files"
library_cards_path: "Library 数字图书馆/Cards"
concepts_path: "Concepts 概念与理论"
permanent_notes_path: "Permanent Notes 永久笔记"
moc_path: "MOC Maps 主题地图"
people_path: "People 人物志"
project_workspace_path: "Projects 项目/学者问道 Scholar-Wendao/{slug} 蒸馏"

examples_retention: "lightweight"  # minimal | lightweight | full

# Phase 0.5 自动填充
coverage_report:
  local_pdfs_count: 0
  expected_books_count: 0
  coverage_percent: 0
  mode: ""                        # 纯网络 | 本地补 | 本地优先 | 纯本地
---
```

完整模板见 [`references/_library_config-template.md`](references/_library_config-template.md)。

### `examples_retention` 策略

| 选项 | 项目仓库 `examples/{slug}-perspective/` 保留 |
|---|---|
| `minimal` | `SKILL.md` + `_vault_paths.md` 索引 |
| `lightweight`（默认） | 上述 + `references/research/` + `_pdf_evidence/_navigator.md` |
| `full` | 全部双份（Vault + 项目仓库；体积大，不推荐） |

---

## 已有案例

### stiegler-perspective（v0.4.1）

[`examples/stiegler-perspective/`](examples/stiegler-perspective/)

| 维度 | 数据 |
|---|---|
| 概念地图 | 6 核心 + 3 次级，全部含证据来源 |
| 一手来源占比 | ~70% |
| Library 增长 | 17 PDF + 17 Cards 落入用户 Vault |
| Vault 同步 | research/biography/pdf_evidence + 6 概念笔记 + MOC + 人物志 全部 wikilink 化 |
| Quality check | 90/100，引文 page-anchor 92% 可证（12/13） |
| 已知 backlog | 5 部扫描 PDF 待 OCR · 41 闭源 book 待 annas（代理出口受限）· 349 部非 book 待 v0.4.2 harvester |

---

## 区别于女娲

[女娲.skill](https://github.com/alchaincyf/nuwa-skill) 证明了"把人的思维框架蒸馏成可调用 skill"是可行的。**学者问道**专为人文社科学者重新设计：

| 女娲 | 学者问道 | 差异理由 |
|---|---|---|
| 默认第一人称扮演 | 默认第三人称分析镜片 | 学者圈最反感把哲学家变成聊天机器 |
| 决策启发式（商业） | 方法论进路 + 立场转变 | 学者没有商业决策但有学术论战 |
| 表达 DNA = 语气模仿 | 行文风格 + 概念语言 | 强调术语使用，避免译者风格污染 |
| 5 项诚实边界 | 6 项（加死亡-尊重边界） | Stiegler/Benjamin/Althusser 案例 |
| 单一产物 SKILL.md | **三大产物**（Library + Skill + KB） | 蒸馏 = 同时建图书馆 |
| 不涉及 Vault | **强制 Vault 同步**（Phase 5.5） | 工具必须进入研究者实际工作流 |

致敬而非取代。本项目方法论受女娲启发，但定位、设计哲学、目标用户均独立。

---

## 安装

```bash
# 1. 装到 Claude Skills
git clone https://github.com/tizzy916/scholar-wendao-skill.git
ln -sfn $(pwd)/scholar-wendao-skill ~/.claude/skills/scholar-wendao-skill

# 2. Python 依赖
pip3 install pymupdf pyyaml requests

# 3. 可选：annas-py（受版权资料获取需要 ANNAS_API_KEY）
pip3 install annas-py

# 4. Library 路径（如果还没有）
export SCHOLAR_WENDAO_LIBRARY="$HOME/.../Library 数字图书馆/_files"
```

---

## 诚实边界 · Humble Epistemics

scholar-wendao 与市面其他人格 skill 的核心差异化：**正面回应六大学术批评**。每个生成的 perspective skill 必须明确包含：

1. **波兰尼问题** —— 默会知识不可蒸馏；本镜片只能复现学者可显式表达的部分
2. **思想化石化** —— 调研时间点的快照；演变需要 update
3. **公开 vs 私下** —— 所有公开材料是经过过滤的展演自我
4. **传记修辞污染** —— 来源等级 + 多源交叉
5. **漫画化风险** —— 警觉用 skill 时是否在生产"段子集合"而非智识分析
6. **死亡-尊重边界**（v0.4 新增） —— 涉及学者自杀 / 监禁 / 重大创伤事件，仅记录可公开核实事实，不戏剧化、不连接因果、不用学者第一人称回应

详见 [`references/humble-epistemics.md`](references/humble-epistemics.md)。

---

## 许可

MIT License. 详见 [LICENSE](LICENSE)。

---

> 致谢 [女娲.skill](https://github.com/alchaincyf/nuwa-skill) 提供方法论启发。
> 创建者：[shencong](https://github.com/shencong)。
