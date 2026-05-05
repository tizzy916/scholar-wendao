# `_library_config.md` 模板 · scholar-wendao v0.4.1

> 本文件是 Phase 0.5 写入每个学者案例的 `_library_config.md` 的标准模板。
> Phase 5.5 (Vault 同步) 与 Phase 6 (GitHub 工作流) 都从此读取。
>
> 字段说明在 frontmatter；案例内的 `_library_config.md` 应使用此模板。

---

## 标准 frontmatter（Phase 0.5 必填）

```yaml
---
# === 学者标识 ===
scholar_slug: ""             # 用于文件命名（小写无空格，如 "stiegler"、"foucault"、"yuk-hui"）
scholar_name: ""             # 中文/原语全名（用于 People 笔记路径，如 "贝尔纳·斯蒂格勒"）
scholar_name_en: ""          # 英文全名（如 "Bernard Stiegler"）
scholar_birth_year: 0
scholar_death_year: null     # 已故学者填年份；在世留 null

# === 调研时间窗 ===
research_started_at: ""      # ISO date，如 "2026-05-05"
research_completed_at: ""

# === 项目仓库（路径 A，轻产物）===
project_repo_path: ""        # scholar-wendao 项目仓库本地路径
example_path: ""             # examples/{slug}-perspective/ 在仓库内的路径

# === Library 归档（路径 B，重材料；用户的现有图书馆）===
library_root: ""             # Library 根目录绝对路径，如 "$HOME/.../Library 数字图书馆"
archive_layout: "flat"       # "flat" | "by-language"
file_prefix: ""              # 扁平命名前缀（如 "Stiegler"），by-language 模式留空

# === Vault 同步（v0.4.1 · Phase 5.5 必读）===
vault_archive_path: ""           # 用户 Vault 内的"知识库"根（如 "$HOME/.../02 · Knowledge"）
library_files_path: "Library/_files"           # PDF 落点（相对 vault_archive_path）
library_cards_path: "Library/Cards"             # Library Card .md 落点
concepts_path: "Concepts"                       # 概念笔记落点（仅追加，不创建新概念笔记）
permanent_notes_path: "Permanent Notes"         # 谱系永久笔记落点（仅追加）
moc_path: "MOC Maps"                            # 主题地图落点
people_path: "People"                           # 人物志落点
project_workspace_path: "Projects/scholar-wendao/{slug}"   # research/ + biography/ 落点

# === 项目仓库瘦身策略（v0.4.1） ===
examples_retention: "lightweight"   # "minimal" | "lightweight" | "full"
# minimal:   examples/{slug}-perspective/ 只保留 SKILL.md + _vault_paths.md
# lightweight: 默认；额外保留 references/research/ + _pdf_evidence/_navigator.md
# full:      保留所有（与 Vault 双份；不推荐，体积大）

# === Phase 0.5 自动扫描结果 ===
coverage_report:
  local_pdfs_count: 0
  expected_books_count: 0    # 估算：从主要专著清单算
  coverage_percent: 0
  mode: ""                   # "纯网络" | "本地补" | "本地优先" | "纯本地"

# === Phase 1 资料采集结果 ===
harvest_summary:
  total_works_openalex: 0
  books: 0                   # type="book"
  serials: 0                 # type="article" / "proceedings"
  oa_count: 0
  oa_downloaded: 0
  closed_count: 0
  lectures_youtube: 0        # v0.4.1 harvest_lectures.py 输出
  french_journals: 0         # v0.4.1 harvest_french_journals.py
  homepages_links: 0         # v0.4.1 harvest_homepages.py
  collective_works: 0        # v0.4.1 harvest_collectives.py
---
```

---

## 关键决策记录小节（Phase 0.5 后续可手写）

> 每个学者案例都应在 frontmatter 之后用 markdown 写下：
>
> 1. **archive_layout 决策依据**：用户的 Library 是 flat 还是 by-language？为什么这样选？
> 2. **scholar_name 多语种映射**：中文译名、英文名、原语名（必要时含罗马化）
> 3. **scholar_death_year 影响**：已故学者一次性蒸馏、在世学者建议 update 周期
> 4. **vault_archive_path 检查**：是否含空格、是否已存在 Library/Concepts/MOC 等子目录
> 5. **特殊禁忌**：根据 humble-epistemics 第六项（死亡-尊重边界）声明，本学者是否有自杀 / 监禁 / 重大创伤事件需特别处理

---

## examples_retention 选项含义

| 选项 | 项目仓库 examples/{slug}/ 保留 | 用途 |
|---|---|---|
| `minimal` | SKILL.md + `_vault_paths.md` | 极简 demo；GitHub 访客只看到 perspective skill 与 Vault 路径索引 |
| `lightweight`（默认） | 上述 + `references/research/` 7 篇 + `_pdf_evidence/_navigator.md` | 开源访客可看到产出形态，但材料真源在 Vault |
| `full` | 全部素材双份 | 不推荐；用于在没有 Vault 的开源用户场景 |

`Phase 5.5` 根据此字段决定项目仓库瘦身行为；`Phase 6` 提交时只 stage 该字段允许的文件。
