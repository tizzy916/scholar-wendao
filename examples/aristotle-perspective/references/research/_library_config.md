---
# === 学者标识 ===
scholar_slug: "aristotle"
scholar_name: "亚里士多德"
scholar_name_en: "Aristotle"
scholar_name_grc: "Ἀριστοτέλης"     # 古希腊原文名
scholar_birth_year: -384             # 公元前 384 年
scholar_death_year: -322             # 公元前 322 年

# === v0.5 学者类型分流 ===
scholar_type: "traditional"          # 已形成 2300+ 年多派解读传统
default_output_mode: "multi_perspective"

# === 调研时间窗 ===
research_started_at: "2026-05-05"
research_completed_at: ""

# === 项目仓库 ===
project_repo_path: "/Users/shencong/Desktop/scholar-wendao-skill"
example_path: "examples/aristotle-perspective"

# === Library 归档 ===
library_root: "/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆"
archive_layout: "flat"
file_prefix: "Aristotle"             # 一手用 Aristotle{year}_{slug}_{lang}.pdf
school_prefix_pattern: "{Author}_{year}_{slug}_{lang}.pdf"   # 派学者代表作单独命名

# === Vault 同步(沿用 Stiegler 配置)===
vault_archive_path: "/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库"
library_files_path: "Library 数字图书馆/_files"
library_cards_path: "Library 数字图书馆/Cards"
concepts_path: "Concepts 概念与理论"
permanent_notes_path: "Permanent Notes 永久笔记"
moc_path: "MOC Maps 主题地图"
people_path: "People 人物志"
project_workspace_path: "Projects 项目/学者问道 Scholar-Wendao/Aristotle 蒸馏"

examples_retention: "lightweight"

# === v0.5 古典引文系统 ===
classical_citation_system: "bekker"
# Bekker 编号格式: NNN[abcd]NN, e.g. 1097b22, 1098a20-b30
# 标准缩写: EN (Nicomachean Ethics) / Pol. (Politics) / Met. (Metaphysics)
#         / Phys. (Physics) / Poet. (Poetics) / Rhet. (Rhetoric)
#         / Cat. (Categories) / DA (De Anima) / DI (De Interpretatione)

# === v0.5 核心 Lineages(4 派,见 references/lineages/ 详细文件)===
lineages:
  - name: "经院派 / Thomism"
    representative: "Thomas Aquinas"
    period: "13世纪 (1225-1274)"
    key_works:
      - "Sententia super Ethica (Commentary on Nicomachean Ethics)"
      - "Summa Theologiae (Prima Secundae)"
      - "Quaestiones Disputatae de Anima"
    reading_strategy: "把 Aristotle 形质论 / 四因说 / 灵魂论整合进基督教神学；通过 essentia/esse 区分 + 自然/超自然分层让 Aristotle 服务 sacra doctrina"
    distinctive_claims:
      - "首要 ousia = essentia + esse(esse 来自上帝创造)"
      - "灵魂作为实体形式但 intellectus possibilis 不朽"
      - "德性二分:acquired virtue + infused virtue"
      - "eudaimonia 终指向 visio beatifica"
    representative_concept_reading:
      ousia: "essentia + esse"
      virtue: "acquired + infused 二分"
      psyche: "实体形式 + 不朽 intellect"
      telos: "自然 telos + 超自然 telos(visio beatifica)"

  - name: "阿拉伯派 / Falsafa"
    representative: "Avicenna (Ibn Sina)"
    period: "10-11世纪 (980-1037)"
    key_works:
      - "Kitāb al-Shifā' (The Book of Healing)"
      - "Kitāb al-Najāt (The Book of Salvation)"
      - "Risāla fī al-ʿishq"
    reading_strategy: "把 Aristotle + 新柏拉图 + 伊斯兰一神论合成;首创 essence/existence 区分 + Necessary Being 论证"
    distinctive_claims:
      - "essence ≠ existence(本质先于存在)"
      - "灵魂作为独立实体(不只是身体形式)"
      - "Active Intellect 是宇宙级独立实体"
      - "首要原理:必然存在(wājib al-wujūd)"
    representative_concept_reading:
      ousia: "essence(分离于 existence)"
      psyche: "独立实体 + 与 Active Intellect 联通"
      potentiality: "受动 vs 主动 potentialities 严格分别"

  - name: "海德格尔派 / Phenomenology"
    representative: "Martin Heidegger"
    period: "20世纪 (1889-1976)"
    key_works:
      - "Sein und Zeit (1927)"
      - "Aristoteles, Metaphysik IX 1-3 (Freiburg lecture, 1931)"
      - "Phänomenologische Interpretationen zu Aristoteles (1922, 'Natorp report')"
    reading_strategy: "回到 Aristotle 的 physis/aletheia/ousia 原始意义,揭示西方哲学史如何把这些概念遗忘为 metaphysica generalis;Aristotle 是'存在论开端'而非'实体论祖师'"
    distinctive_claims:
      - "ousia 原义 = anwesen(在场),被传统遮蔽为 substance"
      - "aletheia = 解蔽,比'真理'(correspondence)更原始"
      - "phronesis 优先于 episteme"
      - "Aristotle Phys. II 是西方对 physis 最后真实把握"
    representative_concept_reading:
      ousia: "anwesen(在场)"
      aletheia: "解蔽(unconcealment)"
      phronesis: "本真存在的实践理解"
      physis: "自身涌现"

  - name: "Anglo-American Analytic / Neo-Aristotelian"
    representative: "Alasdair MacIntyre"
    period: "20-21世纪 (1929-)"
    key_works:
      - "After Virtue (1981)"
      - "Whose Justice? Which Rationality? (1988)"
      - "Dependent Rational Animals (1999)"
    reading_strategy: "用分析哲学工具复兴 Aristotle 德性论;通过 narrative + practice + tradition 三层结构论证启蒙以来道德哲学失败必须回到 Aristotelian framework"
    distinctive_claims:
      - "德性 ≠ trait,是 practice 内部 goods 的获取条件"
      - "narrative unity of human life 是德性可理解前提"
      - "tradition 是 rationality 的载体(对启蒙的 universal reason 反对)"
      - "现代道德哲学是 Aristotelian framework 崩溃后的碎片"
    representative_concept_reading:
      virtue: "practice 内部 goods 的获取条件"
      eudaimonia: "narrative 中 'good life' 整体性"
      telos: "biological + social 双层 telos"
      practical_wisdom: "tradition-bound rationality"

# === 次级影响线(参考,不计入主 lineages 4-6)===
secondary_lineages:
  - "新柏拉图派 (Plotinus / Porphyry,3 世纪) - 把 Aristotle 整合进 Plotinian metaphysics"
  - "犹太派 (Maimonides,12 世纪) - 与 Avicenna 平行,影响阿奎那"
  - "Averroes / 拉丁 Averroism (12-13 世纪) - 与阿奎那论争 intellectus 单一性"
  - "Suárez 与晚期经院 (16-17 世纪) - 对近代哲学的桥梁"
  - "黑格尔派 - Hegel 在 Encyclopedia / Logic 中的 Aristotle 重读"

# === Phase 0.5 自动扫描结果 ===
coverage_report:
  local_pdfs_count: 0
  expected_books_count: 30        # Aristotle 主要著作 + 4 派代表作 + 重要二手
  coverage_percent: 0
  mode: "纯网络"

# === Phase 1 资料采集结果(待跑)===
harvest_summary:
  total_works_openalex: 0
  books: 0
  serials: 0
  oa_count: 0
  oa_downloaded: 0
  oa_publishers_found: 0           # v0.4.3 harvest_oa_publishers
  closed_count: 0

# === 死亡-尊重边界(v0.4) ===
death_respect_required: false       # Aristotle 自然死亡 322 BC,无敏感事件
death_respect_note: |
  Aristotle 死亡相对自然(肠胃疾病或自杀,史料分歧),无戏剧化叙事。
  注意是 Aristotle 流亡卡尔基斯(Chalcis,322 BC)前夕去世,流亡是因雅典反马其顿
  情绪。BRACKETING:事实层(322 BC 死于 Chalcis)+ 叙事层(后世某些传记把流亡-死
  亡浪漫化为"哲学家在政治冲突中的退守")。

# === 派学者投射边界(v0.5 第 7 honest bound) ===
lineage_projection_required: true
lineage_projection_note: |
  4 派 lineages 的 reading strategy 是各派的"创造性误读"(Bloom 意义上),不是
  Aristotle 本人内在意图。multi-perspective 输出时严格区分:
  - 「Aristotle 本人怎么看 X」 → 必须基于 A+/A/A- 等级原文(古希腊文 + 权威译本)
  - 「X 派(如 Aquinas)怎么看 X」 → 该派代表作引文 + 该派 reading strategy 锚点
  禁止把 Aquinas 的 reading 转述为 Aristotle 本人立场。
---

# Library 路径配置 · aristotle-perspective (v0.5 traditional)

**调研时间**:2026-05-05
**Skill 产物路径(A)**:`~/Desktop/scholar-wendao-skill/examples/aristotle-perspective/`
**Library 重材料路径(B)**:用户已有的 Obsidian 数字图书馆(Aristotle 一手 + 4 派代表作)

## 关键决策

### 学者类型:traditional

Aristotle 满足 v0.5 traditional 全部判定条件:
- 去世 ≥ 100 年(322 BC,2300+ 年)
- 维基百科/SEP 等已有"interpretation by school"分类
- 著作存在多语种古译本(希腊文 + 拉丁中世纪 + 阿拉伯)
- 已形成至少 4 派系统解读传统

→ Workflow B 走 B.3b 路径(lineages 一等公民 + 概念×派矩阵 + multi-perspective 默认输出)

### 4 主派 + 5 次级影响线

主派覆盖中世纪基督教(经院 / Aquinas)、伊斯兰(阿拉伯 / Avicenna)、20 世纪欧陆(海德格尔)、20-21 世纪英美(MacIntyre 后分析派)— 这是 Aristotle 接受史的 minimum set。次级影响线作为参考(不深度蒸馏)。

### 古典引文:Bekker 编号

Aristotle 全集标准引文用 Bekker(Immanuel Bekker 1831 编 Berlin Academy Aristoteles Graece)边码,如 *EN* 1097b22-1098a20。每条引文必须**双重锚点**:Bekker 编号 + 现代权威译本(如 Ross 译 / Loeb 双语版 / 中译商务馆)页码。

quality_check.py v0.5 已支持 Bekker 正则识别。

### 派学者投射边界

v0.5 第 7 honest bound 必填。Aristotle 是被各派"创造性误读"最严重的哲学家之一,框架必须显式声明:
- 「Aristotle 怎么看 X」≠「Aquinas 笔下的 Aristotle 怎么看 X」
- multi-perspective 输出格式中,每派的 reading 必须有该派代表作引文锚点(防止 LLM 跨派混淆)

## 待获取(Phase 1 待跑)

### Aristotle 一手(P0,Tier 1-2 OA 应该多)
- *Nicomachean Ethics* (NE / EN)
- *Politics* (Pol.)
- *Metaphysics* (Met.)
- *Physics* (Phys.)
- *De Anima* (DA)
- *Poetics* (Poet.)
- *Rhetoric* (Rhet.)
- *Categories* + *De Interpretatione* (Cat. + DI, 工具论)
- *Posterior Analytics* (APo)

### 派学者代表作(P1,Tier 2-3)
- Aquinas: *Summa Theologiae* (Prima Secundae) + *Sententia super Ethica*
- Avicenna: *Kitāb al-Shifā'* (Healing) — 伊斯兰哲学权威英译可能 OA
- Heidegger: *Sein und Zeit* + *Phänomenologische Interpretationen zu Aristoteles*
- MacIntyre: *After Virtue* + *Whose Justice?*

### 重要二手(P2)
- Sorabji *Aristotle Transformed* (1990)
- Cambridge Companion to Aristotle
- Annas *The Morality of Happiness*
- Nussbaum *The Fragility of Goodness*
