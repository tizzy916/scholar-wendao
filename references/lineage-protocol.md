# Lineage Protocol · 传统学者派别提炼规范（v0.5）

> **scholar-wendao v0.5 核心新增结构**：
> 传统学者(`scholar_type: traditional`)的 SKILL.md 必须含 **lineages 章节**，
> 把 2300 年解读传统结构化为 4-6 派可调用 reading strategy。
>
> 本协议是 Phase B.3' 的操作规范，与 `biography-protocol.md`(当代学者)并列。

---

## 一、为什么 lineages 是一等公民

### 当代学者 vs 传统学者的根本差异

| | 当代单一作者 | **传统学者** |
|---|---|---|
| 作者-思想耦合 | 1 作者 = 1 思想 | 1 作者 = N 派 reading |
| "二手" 性质 | 学术研究/书评 | **派学者本人著作（子一手）** |
| 概念定义稳定性 | 作者定义即权威 | **每派对核心概念定义不同** |
| 时间窗 | 单一 active 时期 | **2000+ 年传承持续重读** |
| 用户提问 "X 会怎么看 Y" | 单一答案 | **本人 + N 派 N 答案** |

举例：问"Aristotle 怎么看 AI 自动化对德性的影响?"
- v0.4.x framework：单一答案(基于 Aristotle 本人著作直接推断)
- v0.5 traditional：
  - **本人**（基于 *EN* 1103b14：德性是 hexis(习惯化能力)，由 ergon 实现）
  - **Thomas Aquinas / 经院派**：(他会引 *Summa Th.* I-II Q.49-54 论 habit；自动化短路了 actus humanus 的 deliberation 环节，威胁 acquired virtue 但不威胁 infused virtue)
  - **Heidegger 派**：(技术作为 *Gestell* 把 *physis* 还原为 standing-reserve；德性的 *aletheia* 维度被遮蔽)
  - **MacIntyre / 后分析派**：(自动化破坏了 practice 的内部 goods，从而摧毁 virtue traditions)

四个回答互相不可替代，每个都需要**该派 reading strategy 的精确蒸馏**。

---

## 二、Lineages 的来源等级（v0.5 新增 + 扩展 v0.4 八等级）

| 等级 | 来源 | 说明 |
|---|---|---|
| **A+** | 学者本人原文(原语) | Aristotle 希腊文,Plato 希腊文,Confucius 古汉语 |
| **A** | 学者本人原文(权威古译) | Aristotle 拉丁中世纪译本(Robert Grosseteste / William of Moerbeke)|
| **A-** | 学者本人原文(现代权威译本) | Bywater 编 OCT, Loeb 双语版,Ross 译,商务印书馆中译 |
| **A^**（v0.5 新增） | **派学者本人著作中的"子一手"reading** | Aquinas *Sententia super Ethica*(他的 Aristotle 注疏),Avicenna *Shifa* |
| B+ | 派学者权威综述 | MacIntyre *After Virtue*,Sorabji *Aristotle Transformed* |
| B | 现代学术研究专著 | Cambridge Companion to Aristotle |
| B- | 学位论文 / 研讨会论文集 | |
| C+ | 教科书 / 入门书 | |
| C | 维基百科 / 通识介绍 | 仅做 cross-reference 不作权威 |

**A^ 是 v0.5 关键新增**：派学者亲自蒸馏过的 Aristotle reading 比一般的二手研究权重高，因为它本身在历史上塑造了"X 派的 Aristotle"这个对象。

---

## 三、Lineage 提炼的 6 个必填字段

每派 lineage 必须填以下 6 个字段：

```yaml
- name: ""                   # 中英双语，如 "经院派 / Thomism"
  representative: ""         # 单代表学者全名，如 "Thomas Aquinas"
  period: ""                 # 该派活跃期，如 "13世纪" / "10-12世纪"
  key_works: []              # 1-3 部代表作（书名或文集）
  reading_strategy: ""       # 一句话：该派如何"读" Aristotle/Plato/...
  distinctive_claims: []     # 3-5 条该派与其他派的核心差异点
  representative_concept_reading: {}   # 该派对 N 个核心概念的 specific reading
```

### 例 · Aristotle 的 4 派 lineages

```yaml
lineages:
  - name: "经院派 / Thomism"
    representative: "Thomas Aquinas"
    period: "13世纪 (1225-1274)"
    key_works:
      - "Summa Theologiae"
      - "Sententia super Ethica (Commentary on Nicomachean Ethics)"
      - "Quaestiones Disputatae de Anima"
    reading_strategy: "把 Aristotle 形质论 / 四因说 / 灵魂论整合进基督教神学；通过区分自然 / 超自然，让 Aristotle 服务于 sacra doctrina"
    distinctive_claims:
      - "首要 ousia = essentia + esse(存在)，esse 来自上帝创造"
      - "灵魂作为实体形式，但 intellectus possibilis 不依赖于身体即可不朽"
      - "德性二分：acquired virtue（自然修习） + infused virtue（神恩注入）"
      - "*eudaimonia* 不只是地上活动，最终指向 visio beatifica"
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
      - "Kitāb al-Najāt"
      - "Risāla fī al-ʿishq (Treatise on Love)"
    reading_strategy: "把 Aristotle + 新柏拉图 + 伊斯兰一神论合成；强调 essence/existence 区分,首创 'Necessary Being' 论证"
    distinctive_claims:
      - "essence ≠ existence(本质先于存在)——后被 Aquinas 继承"
      - "灵魂作为独立实体（不只是身体形式）"
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
      - "Phenomenologische Interpretationen zu Aristoteles (1922)"
    reading_strategy: "回到 Aristotle 的 *physis / aletheia / ousia* 原始意义，揭示西方哲学史如何把这些概念遗忘为 metaphysica generalis；把 Aristotle 读为'存在论的开端'而非'实体论的祖师'"
    distinctive_claims:
      - "ousia 原义 = anwesen(在场)，被传统遮蔽为 substance"
      - "*aletheia* = 解蔽，比'真理'(correspondence) 更原始"
      - "*phronesis* 优先于 *episteme*——存在的实践理解"
      - "Aristotle *Phys.* II 是西方对 *physis* 最后的真实把握，之后被 metaphysica 遮蔽"
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
    reading_strategy: "用分析哲学工具复兴 Aristotle 德性论；通过 narrative + practice + tradition 三层结构,论证启蒙以来道德哲学的失败必须回到 Aristotelian framework"
    distinctive_claims:
      - "德性 ≠ 单独的 trait,而是 practice 内部 goods 的获取条件"
      - "narrative unity of human life 是德性可理解的前提"
      - "tradition 是 rationality 的载体(对启蒙的 universal reason 反对)"
      - "现代道德哲学(Kant/utilitarian)是 Aristotelian framework 崩溃后的碎片"
    representative_concept_reading:
      virtue: "practice 内部 goods 的获取条件"
      eudaimonia: "narrative 中 'good life' 整体性"
      telos: "biological + social 双层 telos"
      practical_wisdom: "tradition-bound rationality"
```

### Lineages 的额外要求（v0.5）

1. **必须 4-6 派**(少于 4 = 维度不足，多于 6 = 信息过载)
2. **必须含至少 1 派当代** + 至少 1 派古典(如 Aristotle 必须有 Aquinas 古典 + MacIntyre 当代)
3. **representative 必须是单一学者**(简短派传统补述放在 reading_strategy / distinctive_claims)
4. **每派必须 distinctively 不同**(否则合并)

---

## 四、Lineages 与概念地图的耦合

v0.5 的概念地图是**「概念 × 派」二维矩阵**而非单一定义。

### 模板

```markdown
### 核心概念 N: {名称}（{原语}）

**本人定义**（基于 *Source* + 古典引文）：
…

**N 派 reading 差异**：

| 派 | 核心 reading | 关键差异 | 引文 |
|---|---|---|---|
| 本人 | … | (基线) | *EN* 1097b22 |
| 经院派 / Aquinas | … | 加 esse 维度 | *Summa Th.* I-II Q.49 |
| 阿拉伯派 / Avicenna | … | essence/existence 分离 | *Shifa* … |
| 海德格尔派 | … | 还原为 anwesen | *Sein und Zeit* §40 |
| 分析派 / MacIntyre | … | practice-bound | *After Virtue* ch.14 |

**为何这些差异重要**：
- 经院派 vs 海德格尔派的 *ousia* 解读差异 = 西方形而上学的两条根本路径
- 实操：用户问"自动化对德性影响"，四派给出**不同实操结论**

**局限**：
…
```

---

## 五、Lineages 的"诚实边界"扩展

humble-epistemics 第六章(v0.4 死亡-尊重边界)已经存在。v0.5 加第七章「**派学者投射边界**」：

> **第七项 · 派学者投射边界**：每派的 reading strategy 是该派的"创造性误读"，
> 不是 Aristotle 本人的内在意图。本镜片输出"X 派会这样看"时，
> 是基于该派学者著作的 reading 推断，**不应被作为 Aristotle 本人立场**。
>
> 用户提问"Aristotle 本人会怎么看"时，工具应回到 A+ 等级原文(原希腊文 + 权威译本)
> 严格作答；提问"X 派会怎么看"时才走 lineage reading strategy。

quality_check.py v0.5 加新检查项：multi-perspective 输出中，每个派的 reading 必须有"该派之所以这样读"的 lineage_strategy 锚点(防止 LLM 混淆派别间界限)。

---

## 六、向后兼容

- 当代学者(`scholar_type: contemporary`)的 SKILL.md **不需要** lineages 章节
- v0.5.2 用 traditional framework 升级 Stiegler 时，加 lineages（海德格尔影响 / Simondon 影响 / Derrida 影响 / 中国 Stiegler 派——许煜/陆兴华），让 Stiegler 也支持 multi-perspective 输出
- 现有 Stiegler 的"智识谱系"章节（v0.4 已有）将作为 lineages 章节的前身，平滑升级
