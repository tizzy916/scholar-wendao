<div align="center">

# 学者问道 · Scholar-Wendao

> *问道于古今学者* · *Ask the way of scholars across time*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Inspired by Nuwa](https://img.shields.io/badge/Inspired%20by-%E5%A5%B3%E5%A8%B2.skill-orange)](https://github.com/alchaincyf/nuwa-skill)

**为人文社科学者构建可调用的"思想分析镜片"的开源框架。**

输入一个学者的名字 → 自动多语言采集著作、二手文献、学术争论、传记 → 提炼出可在你研究中调用的分析工具。

不是 AI 陪聊。不是角色扮演玩具。**是学术分析工具。**

[**Why this exists**](#为什么-为什么不直接用女娲) · [**安装**](#安装) · [**使用**](#使用示例) · [**架构**](#7-1-agent-架构) · [**诚实边界**](#诚实边界--humble-epistemics) · [English](README_EN.md)

</div>

---

## 为什么 · 为什么不直接用女娲？

[女娲.skill](https://github.com/alchaincyf/nuwa-skill) 证明了一件事：把任何人的思维框架蒸馏成可调用的 skill 是可行的。它的方法论（三重验证、表达 DNA、矛盾处理）已被 13+ 人物 skill 验证过。

**但女娲的目标用户是创业者/产品经理/创作者。** 它的设计内含三个学术使用场景天然抗拒的基因：

| 女娲基因 | 学术使用场景为何抗拒 |
|---|---|
| 默认第一人称扮演 | 学者圈最反感的就是把哲学家变成聊天机器 |
| 决策启发式偏向商业 | 学者没有"商业决策"，但有学术立场转变与公开论战 |
| 表达 DNA = 语气模仿 | 译介学者（中文学者读福柯）模仿的是译者风格，不是作者风格 |
| 生平塞进时间线 | 传记对学者比对企业家更重要，应独立成章并严格分级标注 |
| 诚实边界一句带过 | 学者蒸馏要直面波兰尼默会知识、思想化石化等结构性局限 |

**学者问道**专为人文社科学者重新设计：

- ✅ **默认输出第三人称分析镜片**（"从 Stiegler 的 organology 视角看，这个现象的技术外在化逻辑是……"），对话/扮演为 opt-in
- ✅ **概念地图**取代"心智模型"，**方法论进路**取代"决策启发式"
- ✅ **多语言一手文献自动采集**（法/德/英/中等），译本只作参考
- ✅ **生平人格独立成章 + 8 等级信息源分级**（A+ 到 C-）
- ✅ **直面五大学术批评**：默会知识、思想化石化、公开-私下、传记修辞、漫画化

致敬而非取代：本项目方法论受女娲启发，但定位、设计哲学、目标用户均独立。

---

## 它在做什么

人文社科学者真正需要的不是"和福柯聊天"，而是**把福柯的分析镜片装到自己的研究流程里**——读到一段田野材料，能立刻问"用 [学者] 的概念框架看，会怎么解读"。

学者问道蒸馏五个层次：

| 层次 | 内容 |
|---|---|
| **怎么分析** | 概念地图 —— 核心理论术语网络（≥2 部著作中作为分析工具反复使用） |
| **怎么进入** | 方法论进路 —— 碰到 X 类问题/材料的具体步骤 |
| **怎么定位** | 学术坐标 + 智识谱系 —— 学派、师承、横向对话、影响下游 |
| **怎么应战** | 重大论战与立场转变 —— 公开争论暴露的真实判断 |
| **怎么做人** | 人格与处世 —— 独立章节，严格分级标注信息源 |

每个 perspective skill 还包含**最厚的一章**：诚实边界——五大局限的具体声明，提醒用户**这是工具，不是替身**。

---

## 安装

### 安装 scholar-wendao 本身（meta-skill）

```bash
# 安装到 Claude 标准 skill 目录
git clone https://github.com/shencong/scholar-wendao.git ~/.claude/skills/scholar-wendao

# 软链接到通用 agent skill 目录（兼容其他 agent 工具）
ln -sfn ~/.claude/skills/scholar-wendao ~/.agents/skills/scholar-wendao

# 重启 Claude 桌面 / Cowork，让新 skill 被发现
```

### 推荐附加（用于多源信息采集）

```bash
# Academix MCP — 学术 API 聚合（OpenAlex / Crossref / Semantic Scholar / arXiv）
# 见 https://github.com/xingyulu23/Academix

# annas-mcp — Anna's Archive 集成
# 见 https://github.com/iosifache/annas-mcp
```

> 学者问道**不重造采集轮子**——优先调用上述两个已有 MCP，仅在不可用时回落到自实现。

---

## 使用示例

### 示例 1：直接路径——给定学者名

```
> 用学者问道蒸馏 Bernard Stiegler，主要语言法语，目标是给我研究技术哲学时做镜片
```

学者问道会：

1. **Phase 0**：确认 Stiegler 身份（避免重名混淆）+ 问你是否有本地一手语料（Stiegler 法语原版 PDF）
2. **Phase 0.5**：在 `~/.claude/skills/stiegler-perspective/` 建立目录骨架
3. **Phase 1**：启动 7 个并行 agent 采集（专著 / 访谈 / 风格 / 二手 / 论战 / 谱系 / 学术档案）
4. **Phase 1.5**：给你看采集质量摘要，等你确认
5. **Phase 2**：提炼概念地图（[第三持存]、[organology]、[pharmakon] 等）+ 方法论进路
6. **Phase 2.5**：给你看提炼摘要，等你确认
7. **Phase 3**：组装为 stiegler-perspective skill（默认分析镜片模式）
8. **Phase 4**：4 项质量验证（含**漫画化检测**）
9. **Phase 5**：双 agent 精炼（含学术合规审）

### 示例 2：诊断路径——只有研究需求

```
> 我研究农村教育政策，想要一种能看穿话语下权力结构的视角，但不知道该选谁的镜片
```

学者问道会：

1. 通过 1-2 轮追问定位需求（你是要批判教育资本主义？还是研究学校作为规训机构？还是研究教育政策中的话语生产？）
2. 推荐 2-3 个候选学者，每个都说明：
   - 核心镜片（一句话）
   - 为什么适合你
   - 学派定位
   - **局限**（这个视角对你的问题有什么盲区）
   - 语料可获取性
3. 你选定后进入直接路径

### 示例 3：调用已有 perspective skill 分析材料

蒸馏完 Stiegler 后：

```
> 用 stiegler-perspective 分析这段抖音算法推荐的体验描述：[材料]
```

输出（默认分析镜片模式）：

> 从 Stiegler 的 organology 三层视角看，这段体验同时涉及技术层（算法的第三持存机制）、心理层（注意力的工业化）、社会层（资本主义条件下的偏向）。
>
> **运用「pharmakon」概念**：这里的算法既是 cure（满足用户即时偏好）也是 poison（剥夺长期注意力品味）。Stiegler 在《新政治经济学批判》（2009）中明确提出，技术对象的双面性取决于其嵌入的社会关系——这意味着分析重点不应在算法本身，而在它服务的资本积累逻辑。
>
> **超出 Stiegler 公开讨论的范围**：他生前关于短视频算法的具体讨论较少（去世于 2020 年），以下是基于其概念体系的合理推断而非他本人立场……

注意：默认输出**第三人称**、**显式标注调用了哪个概念**、**承认推断 vs 学者明说**。这是学术合规的核心。

### 示例 4：可选 opt-in 对话模式

```
> 切换到对话模式，让我直接和 Stiegler 讨论这个问题
```

学者问道生成的 perspective skill 进入对话模式后**第一句必说**：

> 我以 Stiegler 的视角与你对话，基于公开著作的合理推断，**非本人观点**。本对话不可作为 Stiegler 真实立场被引用。

且全程保持元意识——遇到无法基于公开材料推断的问题，立刻退出角色说"超出范围"。

---

## 7 + 1 Agent 架构

Phase 1 启动 7 个并行 sub-agent，每个负责一个维度：

| Agent | 任务 | 输出 |
|---|---|---|
| 1 | 核心专著与代表论文 | `01-monographs.md` |
| 2 | 学术访谈与公开讲座 | `02-interviews.md` |
| 3 | 行文风格 + 概念语言 | `03-style.md` |
| 4 | 二手文献与学术争论 | `04-secondary.md` |
| 5 | 学术立场转变与公开论战 | `05-debates.md` |
| 6 | 生平传记 + 智识谱系 | `06-genealogy.md` |
| **7** | **多语言全著作清单（学术档案）** | **`07-archive.md`** |
| **+1（独立章节）** | **人格与处世**（不是 agent，但同等重要） | `biography/` 子目录 |

参见 [`_skill-source/SKILL.md`](_skill-source/SKILL.md) 中的完整工作流定义，与女娲 6 agent 的对比详见 [`_skill-source/references/extraction-framework.md`](_skill-source/references/extraction-framework.md) §八。

---

## 诚实边界 · Humble Epistemics

**这是学者问道与市面其他人格 skill 的核心差异化**——市面上几乎没有 skill 正面回应这五个根本性批评：

### 1. 波兰尼问题（默会知识不可蒸馏）

> *"We always know more than we can say."* —— Polanyi

学者的研究**直觉、问题嗅觉、文献品味、判断品味**——这些"做研究的肌肉记忆"——是默会的，**任何 skill 都无法蒸馏**。

→ 学者问道明确声明：本镜片只能复现可显式表达的部分，不替代真正阅读学者原著。

### 2. 思想化石化

学者的思想是流动的。Foucault 早/中/晚三期不同；Stiegler 晚期"逆熵"框架与早期"第三持存"侧重已大不相同。

→ 学者问道强制时间窗标注 + 演化轨迹保留 + 增量更新机制。

### 3. 公开 vs 私下表达

所有公开材料都是**经过过滤的展演自我**——同行评审、编辑筛选、自我审查后的版本。学者私下笔记、与亲密合作者的对话中可能有不同判断。

→ 学者问道对每条信息按 8 等级分级（A+ 到 C-）标注**展演程度**。

### 4. 传记修辞污染

传记作者有叙事偏好——会戏剧化形成性事件、制造因果叙事、产生后见之明。"狱中读哲学"型故事被反复加固。

→ 学者问道生平人格章节强制多源交叉验证 + 区分"事实层"vs"叙事层"，不写线性因果叙事。

### 5. 漫画化（Caricature）

蒸馏过头，学者就成了"标志性术语堆砌器"——满嘴 organology / 满嘴 pharmakon，但没有真正的智识深度。**这是学界拒绝人格 skill 的最核心原因**。

→ 学者问道的 Phase 4 质量验证**专设漫画化检测**，FAIL 必须返工。

完整讨论见 [`_skill-source/references/humble-epistemics.md`](_skill-source/references/humble-epistemics.md)。

---

## 与同类项目的关系

```
nuwa-skill (通用人格蒸馏 meta-skill)
   ├─ 方法论启发了 scholar-wendao（致敬，独立设计）
   └─ 生成的 perspective skill 兼容 nuwa 生态

scholar-wendao (人文学术专用 meta-skill) ← 本项目
   └─ 生成 [scholar]-perspective skill
         ├─ stiegler-perspective
         ├─ foucault-perspective
         └─ ...

skill-distillery (通用 skill 创造工具)
   └─ 相邻产品，定位不同（非人格特化）

academic-research-skills 系列 (帮研究者做研究)
   └─ 方向相反：他们帮你做研究，我们帮你建造做研究用的工具
```

**已经被蒸馏过的学者类先例**（独立项目，不是 scholar-wendao 生成）：

- [zizek-skill](https://github.com/JikunR/zizek-skill) —— 齐泽克
- [karlmarx-skill](https://github.com/baojiachen0214/karlmarx-skill) —— 马克思主义方法论
- [mises-perspective](https://github.com/LijiayuDeng/mises-perspective) —— 米塞斯
- [maoxuan-skill](https://github.com/leezythu/maoxuan-skill) —— 毛选方法论
- [feynman-skill](https://github.com/alchaincyf/feynman-skill) —— 费曼

scholar-wendao 不是要替代这些，而是为后续学者蒸馏提供**统一的、学术合规的 meta-工具**。

---

## 项目结构

```
scholar-wendao/
├── SKILL.md                          # 主工作流（5 阶段 + 7 agent + 默认分析镜片模式）
├── references/
│   ├── extraction-framework.md       # 学者版三重验证方法论
│   ├── scholar-template.md           # 学者 perspective skill 输出模板
│   ├── humble-epistemics.md          # 五大批评回应（核心差异化）
│   ├── source-strategies.md          # 各语种各学科信息源策略
│   └── biography-protocol.md         # 生平人格采集规范与伦理
├── scripts/
│   ├── harvest_works.py              # 包装 Academix MCP，多源元数据采集
│   ├── download_open_access.sh       # 开放获取资源批量下载
│   ├── annas_acquire.py              # 包装 annas-mcp，多语言版本优先级
│   ├── biography_synth.py            # 生平人格素材整合
│   └── quality_check.py              # 质量自检（含漫画化检测）
├── examples/
│   └── stiegler-perspective/         # 测试样本（v0.2 加入）
├── README.md / README_EN.md
├── CONTRIBUTING.md
└── LICENSE                           # MIT
```

---

## 路线图

### v0.1 · 设计与方法论 ✅
- [x] 设计原则与思路文档
- [x] SKILL.md 主工作流
- [x] 5 个 references 文档（含 humble-epistemics 核心差异化）
- [x] Prior art 调研
- [x] README + LICENSE

### v0.2 · 实现 🚧
- [ ] scripts/harvest_works.py（包装 Academix）
- [ ] scripts/download_open_access.sh
- [ ] scripts/annas_acquire.py（包装 annas-mcp）
- [ ] scripts/biography_synth.py
- [ ] scripts/quality_check.py（含漫画化检测）

### v0.3 · 验证 📋
- [ ] 用 scholar-wendao 实战蒸馏 Bernard Stiegler
- [ ] stiegler-perspective skill 作为 examples/ 的首个验证样本
- [ ] 与已有 Stiegler 研究材料交叉验证

### v0.4 · 生态 📋
- [ ] 蒸馏 2-3 位不同类型学者作为 examples（如 Charles Taylor / 中国当代学者 / 经典学者）
- [ ] 投递到 [awesome-persona-distill-skills](https://github.com/xixu-me/awesome-persona-distill-skills)
- [ ] 完善 CONTRIBUTING 与 issue templates

### v1.0 · 学界邀请 📋
- [ ] 邀请人文学者使用并反馈
- [ ] 撰写一篇论文记录方法论
- [ ] 探索学者本人/学派代表 review 机制

---

## 贡献

欢迎以下类型的贡献：

1. **生成新的 perspective skill** —— 用 scholar-wendao 蒸馏一位学者，提交到 examples/，附调研数据
2. **改进 references 方法论** —— 五大批评回应的更深入处理、新发现的批评的回应
3. **新增信息源策略** —— 你熟悉的学科 / 语种的特殊档案库
4. **改进采集脚本** —— Academix / annas-mcp 包装的优化、新数据源的加入
5. **学术合规审查** —— 帮我们审视已有 perspective skill 是否真的符合学术规范

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 致谢

- [女娲.skill](https://github.com/alchaincyf/nuwa-skill) —— 方法论启发
- [Academix](https://github.com/xingyulu23/Academix) —— 学术 API 聚合
- [annas-mcp](https://github.com/iosifache/annas-mcp) —— Anna's Archive 集成
- [awesome-persona-distill-skills](https://github.com/xixu-me/awesome-persona-distill-skills) —— 人格蒸馏 skill 生态汇总
- [PersonaLLM Workshop @ NeurIPS 2025](https://personallmworkshop.github.io/) —— LLM persona 学术讨论的重要参考

特别感谢人文社科学者社区——你们的批评精神是让这个 skill 不变成漫画化玩具的最重要外部约束。

---

## 关于作者

**shencong** ——清华大学人文社科研究者

- 研究方向：技术哲学、文化研究、AI 伦理
- 个人项目：[GitHub](https://github.com/shencong)

> *学者问道生成的 skill 不是替代学者，是把他的分析镜片借给你。*
> *用别人的概念地图，看自己的研究材料；用别人的方法论，问自己未问的问题。*
> *不为了模仿他们，是为了拓展你的思维边界——这是与古今学者建立的真正学术对话。*

---

## 许可证

MIT License。详见 [LICENSE](LICENSE)。

随便用、随便改、随便分发——但若公开使用本工具生成的 perspective skill 进行学术研究，建议在方法论部分注明使用了学者问道。

---

<div align="center">

**女娲.skill** 蒸馏了人怎么想。<br>
**学者问道** 蒸馏了学者怎么分析。<br><br>
*用学者的镜片，看你自己的问题。*

<br>

MIT License © 2026 shencong · Inspired by [花叔 Huashu](https://github.com/alchaincyf)'s [女娲.skill](https://github.com/alchaincyf/nuwa-skill)

</div>
