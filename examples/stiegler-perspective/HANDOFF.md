# HANDOFF · Cowork → Claude Code · stiegler-perspective v0.3

> 本文档由 Cowork 会话生成,交接给 Claude Code 在 host 终端继续。
> 生成时间:2026-05-05

## 当前状态(已完成)

✅ **v0.3 stiegler-perspective skill 主体完成**
- 位置:`~/Desktop/scholar-wendao-skill/examples/stiegler-perspective/`
- 静态质量检查:**100/100**
- 漫画化检测:**PASS(边缘 80/100)**——已在激活规则增加术语密度自检约束
- 一手来源占比 ≈70%

✅ **核心概念地图**(6 个 ground-truth 全覆盖 + 3 个次级)
- 第三持存 / 后种系生成 / 药理学 / 普遍器官学 / 象征的贫困 / 废人化
- 次级:文法化 / 中断 / 逆熵

✅ **目录结构**(双路径架构)
```
examples/stiegler-perspective/
├── SKILL.md                          # 47KB / 769 行 主产物
├── HANDOFF.md                        # 本文档
├── _commit_v0.3.sh                   # 一键 commit + 软链脚本
├── _v0.4_iteration_notes.md          # 15 项框架迭代清单(P0-P5)
└── references/
    ├── research/
    │   ├── 01-monographs.md          # 7 系列专著盘点
    │   ├── 02-interviews.md          # 访谈与讲座
    │   ├── 03-style.md               # 行文风格 + 概念语言
    │   ├── 04-secondary.md           # 二手研究 + 主要批评
    │   ├── 05-debates.md             # 论战与立场转变
    │   ├── 06-genealogy.md           # 智识谱系
    │   ├── 07-archive.md / .json     # OpenAlex 395 部元数据
    │   ├── _strategy.md              # 源策略
    │   ├── _library_config.md        # Library 路径配置
    │   ├── _acquisition_manifest.md  # 闭源待获取 46 部 books
    │   └── _oa_download_log.json     # OA 下载日志(成功 12,失败 30)
    └── biography/
        ├── timeline.md
        ├── personality.md
        ├── relations.md
        └── controversies.md
```

✅ **Library 一手 PDF**:从 8 部增至 **17 部** Stiegler PDF
- `~/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/_files/Stiegler*.pdf`
- 沙箱新下:Stiegler2010_Le_circuit_du_désir_musical_fr (2.3MB)、Stiegler2020_Nanjing_Lectures_2016_2019、Stiegler2014_Uncontrollable_Societies、Stiegler2017_Contents/Frontmatter/Notes、Stiegler2022_Une_limite_fr、Stiegler2025_Towards_a_New_Industrial_Revolution、Stiegler2003_De_l_actualité_fr 等

✅ **Obsidian 集成**:已在 `斯蒂格勒研究 MOC.md` 加 `📎 外部资源` 链接段

---

## 待办(3 件,Claude Code 可直接跑)

### 1. ⚠️ Git commit + push(高优先级)

v0.3 还没推到 GitHub。沙箱无权写 `.git/`。

```bash
cd ~/Desktop/scholar-wendao-skill
bash examples/stiegler-perspective/_commit_v0.3.sh
```

脚本会:
- 清掉沙箱遗留的 `.git/index.lock`
- 在 `~/.claude/skills/stiegler-perspective` 创建软链(指向 examples 内 canonical)
- `git add examples/` + commit + 询问 y/N push

### 2. 🧹 清理 Library 子目录污染

沙箱跑 `download_open_access.sh` 自动创建了 `_files/fr/` 和 `_files/en/`,违反你扁平命名约定。沙箱无权清理。

```bash
LIB="$HOME/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/_files"

# 删除未完成的 .tmp + 残留 PDF(已在根目录有更规范命名版本)
rm -f "$LIB/fr/"*.tmp
rm -f "$LIB/en/"*.pdf

# 把 fr/ 里有用的 PDF 移到根目录(如有)
if [ -f "$LIB/fr/2022_Stiegler_Une_limite_au-del_de_laquelle_est_linconnu.pdf" ]; then
  mv "$LIB/fr/2022_Stiegler_Une_limite_au-del_de_laquelle_est_linconnu.pdf" \
     "$LIB/Stiegler2022_Une_limite_v2_fr.pdf"
fi

# 删空子目录
rmdir "$LIB/fr" "$LIB/en" 2>/dev/null

# 验证
ls "$LIB" | grep -iE '^fr$|^en$|^zh$' || echo "✓ 已清理"
ls "$LIB"/Stiegler*.pdf | wc -l
```

### 3. 📚 (可选)配 ANNAS_API_KEY 跑闭源获取

- 前置:在 https://annas-archive.org/donate 捐赠获得 API key($5+ /月或一次性 $30+)
- 然后:

```bash
export ANNAS_API_KEY="你的key"
cd ~/Desktop/scholar-wendao-skill
python3 scripts/annas_acquire.py \
  examples/stiegler-perspective/references/research/07-archive.json \
  -o "$HOME/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/_files" \
  --lang-priority fr,en,zh
```

预期获取关键的法语 Galilée 原版:T&T 1/2/3、Misère 1&2、Mécréance 三部曲、Acting Out、Échographies、Bifurquer 等。

---

## 下一阶段:v0.4 框架迭代

**v0.3 已暴露的核心问题**:**蒸馏深度不足**——本次没有真读任何本地 PDF 全文,概念引文页码全部来自用户已整理的 Obsidian Card 摘录。

**完整 15 项改进清单**:见 `_v0.4_iteration_notes.md`。**P0(必做)**:

1. 增加 `extract_pdf_evidence.py` 强制 step——Phase 1 自动抽取每部本地 PDF 的目录/序言/首尾章节到 `_pdf_evidence/{book}.md`
2. SKILL.md 每个核心概念末尾增加"证据来源"链接到 `_pdf_evidence/...`

**v0.4 起跑建议**(给 Claude Code):
- 先在 host 跑完待办 1-2(commit + cleanup)
- 然后 (可选) 待办 3(annas)获取法语原版
- 然后基于 17-50 部 Library 中的 Stiegler PDF 重新做 PDF 全文提取 + Phase 2 二次蒸馏
- 用更新版本与 v0.3 SKILL.md 做 diff,看哪些概念定义/引文/风格特征因为读了原文而改变

---

## 关键事实(Claude Code 应知)

- 本项目源码在 `~/Desktop/scholar-wendao-skill/`,git remote = `https://github.com/tizzy916/scholar-wendao-skill.git`
- Skill 安装位置 = `~/.claude/skills/stiegler-perspective`(应是软链指向 examples/ 内 canonical)
- Library 根目录 = `~/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/_files`(扁平命名:`Stiegler{year}[_{lang}].pdf`)
- Obsidian Vault = `~/Desktop/obsidian/tizzyVault/`
- 6 个 ground-truth 概念笔记 = `02 · Knowledge 知识库/Concepts 概念与理论/{第三持存,普遍器官学,药理学,象征的贫困,废人化,后种系生成}.md`
- 5 个谱系笔记 = `02 · Knowledge 知识库/Permanent Notes 永久笔记/斯蒂格勒与{德里达,西蒙东,海德格尔,朗西埃,芒福德}.md`

## 与 Cowork 会话的差异

- Cowork 沙箱**无权**写 `.git/`、清 `_files/{fr,en}/`、访问 `~/.claude/skills/`、跑长时间网络任务
- Claude Code 在你 host 终端跑,**全部权限可用**——直接 git push、文件 mv、永久 export ANNAS_API_KEY
