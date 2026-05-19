<div align="center">

# 学者问道 · Scholar-Wendao

> *问道于古今学者* · *Ask the way of scholars across time*

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20281929.svg)](https://doi.org/10.5281/zenodo.20281929)
[![Agent-Agnostic](https://img.shields.io/badge/agent-agnostic-blueviolet)](#agent-agnostic--任何-llm-agent-都能用)
[![Inspired by Nuwa](https://img.shields.io/badge/Inspired%20by-%E5%A5%B3%E5%A8%B2.skill-orange)](https://github.com/alchaincyf/nuwa-skill)
[![v0.6](https://img.shields.io/badge/version-v0.6-blue)](#)
[![5 Skills](https://img.shields.io/badge/skills_validated-5-green)](#已有案例)

**一个 agent-agnostic 的、为人文社科研究者准备的、端到端学术研究 + 论文写作工作流系统。**

输入一个学者的名字 → agent 自动多语言多源采集 → PDF 证据提取 → 概念地图蒸馏 → 同时丰富你的图书馆(PDF + Cards)/ 概念笔记 / 主题地图 → 生成可被**任何 LLM agent** 调用的"分析镜片" → 提交到 GitHub。

不是 AI 陪聊。不是角色扮演。**是研究者每天写论文用的工作流。**

[**核心定位**](#agent-agnostic--任何-llm-agent-都能用) · [**三大产物**](#三大产物) · [**用它写论文**](#用-scholar-wendao-写论文--完整工作流) · [**架构**](#双工作流架构) · [**已有案例**](#已有案例) · [**安装**](#安装) · [**诚实边界**](#诚实边界--humble-epistemics) · [English](README_EN.md)

</div>

---

## Agent-Agnostic · 任何 LLM agent 都能用

scholar-wendao **不是某个 agent 平台的专属插件**——它是一套**可被任何 LLM agent 加载执行的标准化工作流**:

| 你的 agent | 怎么用 scholar-wendao |
|---|---|
| **Claude(Code / Desktop / API)** | 软链到 `~/.claude/skills/` 自动加载,触发词激活 |
| **OpenAI ChatGPT(Custom GPTs)** | 上传 SKILL.md 作为 instructions + scripts 作为 actions |
| **Cursor / Windsurf / Cline** | 把 SKILL.md 放到 `.cursorrules` 或 `.windsurfrules` |
| **LangChain / LlamaIndex 自建 agent** | SKILL.md 作为 system prompt,scripts 作为 tools |
| **国产 agent**(豆包 / Kimi / 通义) | SKILL.md 文本上传 + agent 调用本地脚本 |
| **Aider / Continue / 任意 IDE agent** | 项目根放 `SKILL.md` 即可 |
| **完全本地 agent**(Ollama / vLLM) | 同上,任何能读 markdown 的 agent 都行 |

### 为什么 agent-agnostic 是设计前提

- **SKILL.md 是纯 markdown** — 任何 LLM 都能读
- **scripts/*.py 是标准 Python**(`pymupdf` / `pyyaml` / `requests` 三个常见依赖)— 任何 agent 工具调用机制都能跑
- **数据格式开放**(JSON manifest + markdown evidence + YAML config)— 不绑定任何 vendor
- **触发词是中文+英文自然语言** — 不依赖任何特定 agent 的 DSL
- **产物是开放标准**(SKILL.md / Library Cards / Obsidian Vault wikilinks) — 不锁定任何工具

### 当前已实测的 agent 平台

| Agent | 状态 | 验证方式 |
|---|---|---|
| **Claude Code** | ✅ 主开发环境 | 5 个 perspective skill 全部 deploy |
| **Claude Desktop** | ✅ deploy 验证 | 通过 `~/.claude/skills/` 软链加载 |
| **GPT / Cursor / 自建** | ⏳ 理论可用 | 待社区验证(欢迎 PR 报告) |

---

## 这是什么

人文社科研究者(尤其论文作者)面对一个学者的实际工作量包括四件事,过去分散在四套工具里:

| 工作 | 传统工具 | 痛点 |
|---|---|---|
| 1. **资料搜集** | Google Scholar / Zotero / 手动下载 | OA 链接失败率 75%;闭源专著要个个找;非 book 资料(讲座/访谈/集体著作)无统一入口 |
| 2. **PDF 全文阅读** | Adobe / Preview | 17 部书逐本读概念抽取太慢 |
| 3. **思想分析** | 自己写读书笔记 | 重复写"X 的核心概念"段,跨学者难复用 |
| 4. **知识库整合** | Obsidian + 手工 wikilink | 蒸馏完成后再手工把材料归档到图书馆/笔记/MOC,常常拖延 |

**学者问道把这四件事合并成一个 agent 驱动的端到端流程。** 用户的角色降为:决策点确认 + 提供配置参数 + **写出更好的论文**。

---

## 三大产物

每跑一次蒸馏,scholar-wendao **同时**生产三件成品:

### 🏛️ 1. Library 图书馆增长

把多源采集到的 PDF 落入用户既有的扁平命名 Library(如 `Library/_files/{Author}{Year}_{slug}.pdf`),并自动生成符合用户模板的 Library Card(`Library/Cards/{Author}{Year}.md`,含 frontmatter / APA 引用 / 多语言版本表 / 概念命中分布 / Top 引用片段)。

### 🔬 2. Perspective Skill(论文写作的核心资产)

`examples/{slug}-perspective/SKILL.md`:当前学者的可调用分析镜片。包括:

- 3-15 个核心概念(每个含定义、与他人关系、局限、关键引文,引文必须 page-anchor 可证)
- 5-10 条方法论进路(碰到 X 类材料的分析步骤)
- 学术坐标 + 智识谱系(上游 / 横向 / 下游)
- **(v0.5 新增)Lineages**:对古典学者(Aristotle / Arendt 等)是 N 派 reception 传统;对当代学者(Stiegler 等)是 N 个 influence + 接受 lineages
- 重大论战与立场转变
- 人格与处世(独立章节,BRACKETING 双层标注)
- **七大诚实边界**(默会知识 / 化石化 / 公开-私下 / 传记修辞 / 漫画化 / 死亡-尊重 / **派学者投射**)

### 🕸️ 3. Knowledge Base 联结

把蒸馏过程产出的素材**落入用户 Vault 的对应位置**(默认 Obsidian,任何支持 markdown wikilink 的 vault 都行),并在 MOC / 概念笔记 / 谱系笔记 / 人物志中追加 wikilink 索引。

---

## 用 scholar-wendao 写论文 · 完整工作流

> 这是 scholar-wendao 的**核心 use case** — 不是"做一个 agent demo",是"完成一篇博士论文/期刊文章的实际研究流程"。

### 场景:你正在写一篇关于 Stiegler vs Rancière 在数字技术问题上的对比论文

#### Day 1 · 建库
```
你: "为 Bernard Stiegler 建图书馆"
agent: → 跑 Workflow A
   - harvest_works.py 拉 OpenAlex 全部 Stiegler 著作元数据
   - 跑 download_open_access.sh 自动下 OA 部分
   - 输出 _acquisition_manifest.md(列出哪些要手动下)
   → 你浏览器从 OHP / archive.org 找到 OA 版本
你: "我下了 Bifurcate.pdf 和 Neganthropocene.pdf,加进去"
agent: → 跑 intake_manual_pdf.py(自动重命名 + 归档 + 抽 evidence + 生成 Card)
       Library 从 17 → 19 部 PDF
```

#### Day 2 · 蒸馏
```
你: "蒸馏 Stiegler"
agent: → 跑 Workflow B
   - extract_pdf_evidence(19 部 PDF → 概念锚点)
   - 7 agent 并行调研(专著/访谈/风格/二手/论战/谱系/档案)
   - 框架提炼(6 核心概念 + 3 次级 + 4 lineages)
   - 生成 SKILL.md(1117 行)
   - quality_check(100/100 通过)
   - sync_to_vault(回灌 wikilinks 到 6 概念笔记 + MOC + 人物志)
```

#### Day 3+ · 写论文
```
你: "用 Stiegler 视角分析这段 ChatGPT 现象材料"
agent: 调用 stiegler-perspective skill
       → 6 核心概念分析 + 引文 + 局限 + 不要漫画化的自检

你: "用朗西埃检验我斯蒂格勒论点"   ← 跨 skill 协作
agent: 同时调用 stiegler-perspective + ranciere-perspective
       → 显式处理两个学者的不对称关系
       → 输出"朗-斯接口论证"(论文修订专用 entry point)

你: "Aristotle 各派如何看技术与德性"   ← v0.5 multi-perspective
agent: 调用 aristotle-perspective(traditional)
       → 默认 5 段输出(本人 + Aquinas + Avicenna + Heidegger + MacIntyre)
       → 用 Bekker 编号 + 各派代表作引文锚点
```

#### Day N · 补料 + 重蒸
```
你: "我又下了 3 部 Stiegler 法语原版,加进 Stiegler 的库"
agent: → intake_manual_pdf.py × 3 (累积式增长)

你: "重蒸 Stiegler"   ← Library 增长后整体重做
agent: → 旧 SKILL.md 进 _archive/
       → 重跑 Workflow B 全部
       → 概念引文升级为更精确的法语原版页码
```

**这就是 v0.5 双工作流 + 跨 skill 协作的实际写论文流程**。

---

## 双工作流架构

> scholar-wendao 显式分为**两个独立可触发的子工作流** + 共享数据层。每个 Workflow 可单独跑、可重复跑,组合形式由触发词决定。

### 触发词路由

| 用户输入意图 | Workflow | 路径 |
|---|---|---|
| 「**搜集 X 的资料**」/「**为 X 建图书馆**」/ `build-library X` | **A 单跑** | A.0 → A.5 |
| 「**蒸馏 X**」/「**做 X 的分析镜片**」/ `distill X` | **B 单跑** | B.1 → B.6 |
| 「**学者问道 X**」(默认端到端) | **A → B** | 完整流程 |
| 「**重蒸 X**」 | **B 重做模式** | 旧 SKILL.md 进 archive |
| 「**更新 X 的 skill**」 | **B 轻量 update** | 增补不重写 |
| 「**我有 PDF 想加到 X 的库**」 | **A.4 单步** | `intake_manual_pdf.py` |

### Workflow A · 图书馆建设

| Phase | 内容 | 工具 |
|---|---|---|
| **A.0** | 配置(`_library_config.md`)+ Library 覆盖率扫描 | (config) |
| **A.1** | Metadata 全收集("无漏" manifest) | `harvest_works.py` + 多源 harvester |
| **A.2** | Tier 1+2 自动下载(OA / yt-dlp / scrape) | `download_open_access.sh` |
| **A.3** | Tier 3+4 manifest 输出(待手动 / 浏览器助手项) | `annas_acquire.py`(默认 manifest-only) |
| **A.4** | **用户主动导入** ← 一等公民入口 | `intake_manual_pdf.py` |
| **A.5** | 生成 / 增量更新 Library Cards | `generate_library_cards.py` |

### Workflow B · 学者蒸馏(v0.5 双路径)

| Phase | 内容 | 工具 |
|---|---|---|
| **B.0** | scholar_type 判定(`contemporary` / `traditional` / `topic`)| (Phase 0A) |
| **B.1** | extract_pdf_evidence(基于 Library 当前状态) | `extract_pdf_evidence.py` |
| **B.2** | 7 agent 调研(research / biography) | spawn agents |
| **B.3a/b/c** | 框架提炼(按 scholar_type 分支) | (LLM synthesis) |
| **B.4** | SKILL.md 构建 | (template fill) |
| **B.5** | 质量验证(7 项 declarations + page-anchor + bracketing) | `quality_check.py` |
| **B.6** | Vault 同步(回灌 wikilinks) | `sync_to_vault.py` |

### v0.5 学者类型差异

| 维度 | contemporary | **traditional** | topic |
|---|---|---|---|
| 概念地图 size | 3-7 | **5-15** | 5-10 |
| 默认输出 mode | 单一第三人称 | **multi-perspective**(本人+N 派) | 共识+分歧 |
| Lineages 强制 | 否(可选) | **是**(必填 4-6 派) | 否 |
| 引文系统 | PDF page anchor | **+ Bekker / Stephanus / 中典** | page anchor |

### 4 层资料采集架构

| Tier | 自动化 | 适用源 | 工具 |
|---|---|---|---|
| **1 · 完全 API** | 100% | OpenAlex / Crossref / Semantic Scholar / unpaywall | `harvest_works.py` |
| **2 · 友好 scrape** | 90% | OHP / DOAB / archive.org / 学者主页 | `harvest_oa_publishers.py` |
| **3 · 浏览器助手** | 50% | annas / paywall(机构 access)/ Cairn 锁定 | 浏览器 cookies → 工具 |
| **4 · 完全手动** | 0% | annas 严格反爬 / 闭源专著 / 罕见档案 | `intake_manual_pdf.py` |

**核心设计原则**:**"无漏"原则的实操含义是 metadata 无漏,不是 PDF 全到手**。Tier 3+4 资料显式列入 manifest 让用户决策。

---

## 端到端工作流(命令清单)

> 本节面向 agent。每一 Phase 给出**具体命令**与**退出条件**。命令是 Python / Bash,任何 agent 工具调用机制都能跑。

### Phase 0:入口分流

agent 收到用户请求后,按 `SKILL.md` Phase 0 表格判定路径(直接 / 主题 / 诊断),并判定 scholar_type(contemporary / traditional / topic)。

### Phase 0.5:配置

按 [`references/_library_config-template.md`](references/_library_config-template.md) 模板填 frontmatter(13+ 字段),保存到:
`examples/${SLUG}-perspective/references/research/_library_config.md`

关键字段:
- `scholar_type`: `contemporary` / `traditional` / `topic`
- `archive_layout`: `flat`(推荐)/ `by-language`
- `vault_archive_path`: 用户 Vault 的"知识库"根
- `lineages`(traditional 必填 4-6 派,见 [`references/lineage-protocol.md`](references/lineage-protocol.md))

### Phase 1.0:多源信息采集

```bash
# 学术 metadata (OpenAlex / Crossref / Semantic Scholar)
python3 scripts/harvest_works.py "Bernard Stiegler" \
    --output examples/${SLUG}-perspective/references/research/07-archive

# OA 资源批量下载(unpaywall + HTML 落地页 fallback)
bash scripts/download_open_access.sh \
    examples/${SLUG}-perspective/references/research/07-archive.json \
    "${LIBRARY_FILES_DIR}" flat "${PREFIX}"

# Tier 2 OA 出版社 harvester(OHP / DOAB / archive.org)
python3 scripts/harvest_oa_publishers.py "Bernard Stiegler" \
    --output examples/${SLUG}-perspective/references/research/ \
    --slug stiegler --manifest examples/${SLUG}-perspective/references/research/_acquisition_manifest.json
```

### Phase A.4:用户主动导入(可重复入口)

```bash
# 单部
python3 scripts/intake_manual_pdf.py ~/Downloads/Bifurquer.pdf \
    --config examples/${SLUG}-perspective/references/research/_library_config.md \
    --year 2020 --slug Bifurquer --lang fr --execute

# 批量 + auto-infer
python3 scripts/intake_manual_pdf.py ~/Downloads/Stiegler*.pdf \
    --config CONFIG --auto-infer --execute
```

### Phase B.1:PDF Evidence 强制提取

```bash
python3 scripts/extract_pdf_evidence.py \
    --library "${LIBRARY_FILES_DIR}" \
    --filter "${PREFIX}*.pdf" \
    --concepts examples/${SLUG}-perspective/_pdf_evidence/_concepts.json \
    --out examples/${SLUG}-perspective/_pdf_evidence

# 重生 navigator(从 _index.json 自动)
python3 scripts/regenerate_navigator.py \
    --evidence-dir examples/${SLUG}-perspective/_pdf_evidence \
    --scholar-name "Bernard Stiegler"
```

### Phase 2.9:Library Card 生成

```bash
python3 scripts/generate_library_cards.py \
    --config examples/${SLUG}-perspective/references/research/_library_config.md \
    --evidence-dir examples/${SLUG}-perspective/_pdf_evidence \
    --archive-json examples/${SLUG}-perspective/references/research/07-archive.json
```

### Phase 4:质量验证

```bash
python3 scripts/quality_check.py \
    --skill examples/${SLUG}-perspective/SKILL.md \
    --evidence-dir examples/${SLUG}-perspective/_pdf_evidence
```

**v0.5 检查项**:
| 检查 | contemporary | traditional |
|---|---|---|
| 诚实边界声明 | 6 项 | **7 项**(含 lineage 投射) |
| 概念地图 | 3-7 | **3-15** |
| 方法论进路 | ≥ 5 | ≥ 5 |
| 引文 page-anchor | ≥ 80% | ≥ 80%(含 Bekker / Stephanus) |
| Narrative-bracketing | 形成性事件 100% 双标注 | 同 |
| **Lineages**(v0.5) | (可选) | **必填 4-6 派** |
| **Multi-perspective 输出**(v0.5) | (opt-in) | **默认必填** |

### Phase 5.5:Vault 同步

```bash
python3 scripts/sync_to_vault.py \
    --config examples/${SLUG}-perspective/references/research/_library_config.md
# 确认无误后可加 --prune 瘦身项目仓库
```

### Phase 6:GitHub 工作流

```bash
git add SKILL.md scripts/ references/ examples/${SLUG}-perspective/ README.md
git commit -F /tmp/commit_msg.txt
git push origin main

# Optional: 派生为 standalone repo (便于单独分发)
gh repo create ${SLUG}-perspective --public --description "..."
git subtree push --prefix=examples/${SLUG}-perspective \
    https://github.com/USER/${SLUG}-perspective.git main
```

---

## 已有案例

5 个 perspective skill 已通过 quality_check 验证 + deploy 验证:

| Skill | scholar_type | Lineages | 概念 | 行数 | quality | 论文写作用途 |
|---|---|---:|---:|---:|---|---|
| [stiegler-perspective](examples/stiegler-perspective/) | contemporary(+lineages) | 4(影响 3 + 接受 1) | 6+3 | 1117 | **100/100** | 数字技术 / 算法治理 / 平台资本 / 注意力经济 |
| [aristotle-perspective](examples/aristotle-perspective/) | traditional | 4(经院/阿拉伯/海德格尔/分析) | 7 | 707 | **100/100** | 古典德性论 / 政治哲学 / 形而上学 / 城邦理论 |
| ranciere-perspective(待补 examples/) | contemporary | 0(纯 v0.4.x 风格) | 6 | 730 | **95/100** | 美学体制 / 感性分配 / 解放观众 / 平等公理 |
| arendt-perspective(待补 examples/) | traditional | **5** | 14 | 1073 | **90/100** | 公共领域 / 极权主义诊断 / banality of evil / labor-work-action |
| mumford-perspective | (Workflow A 完成,B 未启动) | - | - | - | - | (待蒸) |

**跨 skill 协作示例**:`ranciere-perspective` 显式处理与 `stiegler-perspective` 的不对称关系,含"论文 #06 朗-斯接口论证"专用 entry point — 这是真实学术研究中**两个学者交叉对话**的工程化范式。

### Standalone 分发

每个 perspective skill 都可作为独立 repo 分发(via `git subtree push`):
- [stiegler-perspective](https://github.com/tizzy916/stiegler-perspective) (standalone)
- [aristotle-perspective](https://github.com/tizzy916/aristotle-perspective) (standalone)

任何 agent 用户可直接 `git clone https://github.com/tizzy916/{slug}-perspective.git` 单独使用。

---

## 区别于女娲

[女娲.skill](https://github.com/alchaincyf/nuwa-skill) 证明了"把人的思维框架蒸馏成可调用 skill"是可行的。**学者问道**专为人文社科学者重新设计:

| 女娲 | 学者问道 | 差异理由 |
|---|---|---|
| 默认第一人称扮演 | 默认第三人称分析镜片 | 学者圈最反感把哲学家变成聊天机器 |
| 决策启发式(商业) | 方法论进路 + 立场转变 | 学者没有商业决策但有学术论战 |
| 表达 DNA = 语气模仿 | 行文风格 + 概念语言 | 强调术语使用,避免译者风格污染 |
| 5 项诚实边界 | **7 项**(加死亡-尊重 + 派学者投射) | Stiegler/Benjamin/Althusser 案例 + traditional 学者派别问题 |
| 单一产物 SKILL.md | **三大产物**(Library + Skill + KB) | 蒸馏 = 同时建图书馆 |
| 不涉及 Vault | **强制 Vault 同步**(Phase 5.5) | 工具必须进入研究者实际工作流 |
| 单一作者模型 | **传统学者多视角支持**(v0.5) | 古典学者(Aristotle / Plato / Kant 等)需要 N 派 reading |

致敬而非取代。本项目方法论受女娲启发,但定位、设计哲学、目标用户均独立。

---

## 安装

### 通用步骤(任何 agent)

```bash
# 1. clone 主仓
git clone https://github.com/tizzy916/scholar-wendao-skill.git

# 2. Python 依赖(scripts 用)
pip3 install pymupdf pyyaml requests

# 3. (可选)annas-py(受版权资料获取需要 ANNAS_API_KEY)
pip3 install annas-py

# 4. Library 路径
export SCHOLAR_WENDAO_LIBRARY="$HOME/.../Library 数字图书馆/_files"
```

### Agent 平台特定 deploy

#### Claude(Code / Desktop)

```bash
ln -sfn $(pwd)/scholar-wendao-skill ~/.claude/skills/scholar-wendao-skill
# 重启 Claude
```

触发:任意自然语言含「学者问道 X」/「蒸馏 X」/「为 X 建库」即激活。

#### OpenAI ChatGPT(Custom GPT)

1. ChatGPT → "Create a GPT" → Configure → Instructions → 粘贴 `SKILL.md` 全文
2. Add Actions → 用 OpenAPI schema 包装 `scripts/*.py` 为 HTTP endpoints(或本地 docker container)
3. 触发词在用户对话中自然语言激活

#### Cursor / Windsurf / Cline / Aider

```bash
cp scholar-wendao-skill/SKILL.md /path/to/your/project/.cursorrules
# 或: ln -s scholar-wendao-skill/SKILL.md /path/to/project/.cursorrules
```

scripts 通过 IDE 内 terminal 调用。

#### LangChain / LlamaIndex / 自建 agent

```python
# system prompt
with open("scholar-wendao-skill/SKILL.md") as f:
    system_prompt = f.read()

# tools
from langchain.tools import ShellTool
tools = [
    ShellTool(name="harvest_works", command="python3 scripts/harvest_works.py {scholar}"),
    ShellTool(name="extract_evidence", command="python3 scripts/extract_pdf_evidence.py ..."),
    # ... 所有 scripts/*.py
]
```

---

## 诚实边界 · Humble Epistemics

scholar-wendao 与市面其他人格 skill 的核心差异化:**正面回应七大学术批评**。每个生成的 perspective skill 必须明确包含:

1. **波兰尼问题** —— 默会知识不可蒸馏;本镜片只能复现学者可显式表达的部分
2. **思想化石化** —— 调研时间点的快照;演变需要 update
3. **公开 vs 私下** —— 所有公开材料是经过过滤的展演自我
4. **传记修辞污染** —— 来源等级 + 多源交叉
5. **漫画化风险** —— 警觉用 skill 时是否在生产"段子集合"而非智识分析
6. **死亡-尊重边界**(v0.4) —— 涉及学者自杀 / 监禁 / 重大创伤事件,仅记录可公开核实事实,不戏剧化
7. **派学者投射边界**(v0.5) —— 4-6 派 lineages 的 reading 是各派的"创造性误读",不是学者本人内在意图

详见 [`references/humble-epistemics.md`](references/humble-epistemics.md) + [`references/lineage-protocol.md`](references/lineage-protocol.md)。

---

## 路线图

- ✅ **v0.4.x** · 端到端工作流 + Library 联动 + intake_manual_pdf 一等公民
- ✅ **v0.5.x** · Traditional 学者支持(lineages + multi-perspective + Bekker 引文)
- ⏳ **v0.6** · 跨 skill 协作框架(基于 ranciere↔stiegler 的不对称对话案例文档化)
- ⏳ **v0.7** · `harvest_classical.py`(Perseus / Loeb / Stoa 古典学专项)+ word-boundary _concepts 增强
- ⏳ **v1.0** · 多 agent 平台 deploy 验证(GPT / Cursor / 自建 agent)+ 国际化 + paper-writing dashboard

---

## 关于作者 / About the Author

沈聪,中央美术学院实验艺术学院本科,清华大学科学史系硕士(导师 [胡翌霖](https://yilinhut.net/author/admin)),科技文创公司 [天与视界 TIANYU VISION](https://tianyu.art/) 创始人 & CEO。学术训练横跨实验艺术、科学史与技术哲学;创业方向是用 AI 做科研可视化、科学传播与科艺融合。

「学者问道」诞生于一个具体的写作困境——做学位论文《技术自由主义》时,他不需要"和 Stiegler 聊天",而是需要把多位学者(Stiegler、Rancière、Arendt、Aristotle……)的分析镜片装进自己的研究流程,边读材料边能立刻调用。市面上没有这样的工具,只能自己造——这就是学者问道。

📮 [GitHub @tizzy916](https://github.com/tizzy916) · shencong916@gmail.com · 欢迎纠错、合作、交流

---

## License

**CC BY-NC 4.0**(知识共享 署名-非商业性使用 4.0 国际许可协议)。详见 [LICENSE](LICENSE)。

> ⚠️ **License change (2026-05-19)**:本项目已从 MIT 改为 CC BY-NC 4.0。在此 commit 之前的版本(`67bc174` 及更早)仍按 MIT 协议发布——那些版本及其衍生品保留原始的商用权利。新版本起,**禁止商业用途**。

### 商业用途 / Commercial Use

本 skill 采用 CC BY-NC 4.0 协议——**仅限非商业用途**(学术研究、教学、个人项目、开源衍生)。

如需商业使用(嵌入付费产品、作为付费咨询服务的一部分、商业 SaaS 集成等),请联系作者获取商业 license:

📮 **shencong916@gmail.com**(沈聪 · 天与视界 TIANYU VISION)

作者保留按个案授予商业 license 的权利。

---

> 致谢 [女娲.skill](https://github.com/alchaincyf/nuwa-skill) 提供方法论启发。
>
> *用别人的概念地图,看自己的研究材料;用别人的方法论,问自己未问的问题。*
> *不为了模仿他们,是为了拓展你的思维边界——这是与古今学者建立的真正学术对话。*
