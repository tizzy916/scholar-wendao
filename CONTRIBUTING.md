# Contributing to Scholar-Wendao

> 欢迎贡献。本文档说明如何参与，以及对学术合规的硬性要求。
>
> Welcome contributions. This document describes how to participate, and the academic-compliance hard requirements.

---

## 参与方式 / Ways to Contribute

### 1. 用 scholar-wendao 蒸馏新学者，提交到 examples/

**Use scholar-wendao to distill a new scholar; submit to examples/**

最有价值的贡献是**真正用框架蒸馏一位学者**，把生成的 perspective skill + 完整调研数据 + 你的反思（哪些地方框架表现好、哪些地方需要改进）提交回来。

The most valuable contribution is to **actually distill a scholar with the framework**, then submit the generated perspective skill + full research data + your reflection (what worked, what needs improvement).

#### 提交格式 / Submission format

```
examples/[scholar-name]-perspective/
├── SKILL.md                    # 生成的 perspective skill
├── references/
│   ├── research/               # 完整调研数据（7 个 agent 的输出）
│   ├── biography/              # 生平人格采集
│   └── extraction-notes.md     # 你的提炼笔记（哪些选择、为什么）
├── reflection.md               # 你对框架表现的反思
└── (sources/ 不提交 git，仅本地)
```

#### 必须满足的学术合规要求 / Mandatory academic compliance

1. **五大诚实边界完整声明** —— 在 SKILL.md 中必须有 humble-epistemics 的全部五条
2. **信息源 8 等级标注** —— 每条调研内容标注 A+ / A / B / C 等级
3. **多语言原文优先** —— 译介学者必须基于原语采集（如不能，明确说明限制）
4. **生平章节多源交叉** —— 不写线性因果叙事
5. **通过漫画化检测** —— Phase 4 的 caricature test 必须 PASS
6. **非授权表征声明** —— 必须包含"本镜片不代表学者本人观点"

不满足这些 → PR 会被请求修改。这是学者问道的设计底线。

---

### 2. 改进 references 方法论文档

新发现的学界批评 + 更深入的回应都欢迎：

- 对 humble-epistemics 五大批评的更细致论述
- 新发现的批评（第六、第七大）的回应
- 对 extraction-framework 三重验证的细化
- 对 scholar-template 章节结构的优化建议
- 对 source-strategies 新语种 / 新学科的扩充
- 对 biography-protocol 伦理边界的细化

**写法要求**：方法论文档必须**有具体案例**，不能停在抽象原则。例如不要写"应该尊重学者隐私"，要写"采集 X 类信息时应排除 Y / 处理 Z 时应执行 W 步骤"。

---

### 3. 改进采集脚本

`scripts/` 下的 Python 脚本欢迎以下改进：

- `harvest_works.py`：新增数据源（如新的学术 API、特定学科的专属档案）
- `download_open_access.sh`：处理更多 OA 链接格式
- `annas_acquire.py`：多语言版本优先级算法的改进
- `biography_synth.py`：传记类素材整合的算法改进
- `quality_check.py`：漫画化检测算法改进

**测试要求**：任何脚本改动需附 ≥1 个真实学者的端到端测试（哪怕只是元数据采集，不下载）。

---

### 4. 信息源策略扩充

`references/source-strategies.md` 目前覆盖法/德/英/中四种语种 + 5 个学科。欢迎扩充：

- 新语种（西班牙语、葡萄牙语、阿拉伯语、日语、韩语等）
- 新学科（人类学、宗教学、艺术理论、媒介研究等）
- 特殊场景（如殖民档案处理、小语种学者的特殊困难）

提交时附**至少一个该语种/学科学者的实测**，证明策略真的能工作。

---

### 5. 学术合规审查

帮助审视已有的 perspective skills（自己提交的或别人提交的）是否真的符合学术规范：

- 概念地图是否真的来自 ≥2 部著作？
- 一手来源占比是否 >50%？
- 漫画化检测是否真的通过？
- 五大诚实边界是否清晰？

可通过 PR comment 或 issue 形式提出审查意见。

---

## 不接受的贡献 / What we don't accept

- ❌ **未经实测的"假想"perspective skill**：必须真的跑过 scholar-wendao 全流程
- ❌ **删除诚实边界声明**：五大局限是设计底线，不可删
- ❌ **基于知乎 / 公众号 / 百度百科的中文学者蒸馏**：这是黑名单
- ❌ **第一人称扮演为默认输出**：必须默认第三人称分析镜片
- ❌ **窥探隐私的生平蒸馏**：未公开的私人内容（社交平台、聊天记录等）不采集
- ❌ **学术不端的合理化**：如果 perspective skill 涉及学术不端的学者（如 Heidegger 纳粹问题、Althusser 家庭悲剧），必须公平呈现，不洗白也不批判
- ❌ **不附调研数据的 perspective skill**：调研过程必须透明，不能黑箱

---

## PR 流程 / PR Workflow

1. **Fork + Branch**：从 `main` 分支建你自己的分支，命名建议：`example/[scholar-name]` 或 `feature/[改进内容]`
2. **本地测试**：确保所有改动都能跑通
3. **PR 描述**：清楚说明改动是什么、为什么、影响哪些文件
4. **Linked issues**：如果对应了某个 issue，请 link
5. **Code review**：维护者会从学术合规 + 工程质量两个角度审查
6. **Merge**：合并后会更新 CHANGELOG

---

## Issue 类型 / Issue Templates

- 🐛 Bug report
- ✨ Feature request
- 📚 Methodological discussion (五大批评的延伸 / 新批评的发现)
- 🎓 Distillation review (审查某个 perspective skill 是否合规)
- 🌍 Language/discipline strategy expansion
- 📖 Documentation improvement

---

## 行为准则 / Code of Conduct

学者问道是一个**学术工具**项目。我们尊重：

1. **学者本人的尊严** —— 不窥探隐私、不戏剧化、不漫画化
2. **学界的批评精神** —— 欢迎所有合理批评，包括对项目本身的根本性质疑
3. **学派多元** —— 不偏向任何特定学术传统
4. **政治多元** —— 学者问道蒸馏的对象可能跨越政治光谱，要公平对待

歧视性、人身攻击、无证据的污名化贡献会被拒绝。

---

## 维护与决策 / Maintenance & Governance

目前由 [shencong](https://github.com/shencong) 维护。当贡献者达到一定规模后，会：

- 邀请活跃贡献者作为 co-maintainers
- 建立公开的设计 RFC 流程
- 探索学者本人 / 学派代表 review 机制（v1.0 目标）

---

## 致谢 / Acknowledgments

特别感谢：

- [女娲.skill](https://github.com/alchaincyf/nuwa-skill) 作者花叔——为开源人格蒸馏 skill 生态铺路
- 所有提交反馈的人文学者——你们的批评精神是项目的最重要外部约束

---

> *Scholar-Wendao thrives on critique, not on praise.*
> *学者问道因批评而精进，不因赞美而生长。*
>
> *如果你看到任何与学术合规冲突的地方，请提 issue。这是项目最需要的贡献。*
