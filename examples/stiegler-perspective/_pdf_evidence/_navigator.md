# `_pdf_evidence/` Navigator · v0.4

> 由 `scripts/extract_pdf_evidence.py` 跑出。
> 本目录是 v0.4 Phase 2 二次蒸馏的**强制证据库**——SKILL.md 每个核心概念
> 的定义、引文、风格判断都必须能追溯到这里某一份 `{book}.md` 的某一页。

---

## 一、17 部本地 PDF 评估

### 11 部可机读(直接进入蒸馏)

| 文件名 | 真实书名 / 性质 | 页 | empty | concept hits |
| --- | --- | ---:| ---:| ---:|
| Stiegler2003_De_l_actualité_fr | (法语图书馆员对谈集，含 Stiegler) | 38 | 0 | 0 |
| Stiegler2010_Le_circuit_du_désir_musical_fr | "Le circuit du désir musical"（U Montréal Press, 2004 期刊文章） | 17 | 0 | 17 |
| **Stiegler2013** | **What Makes Life Worth Living: On Pharmacology**（Polity；法语原 2010 *Ce qui fait que la vie vaut la peine d'être vécue*, Flammarion） | 177 | 2 | **156** ⭐ |
| **Stiegler2014** | **Symbolic Misery Vol. 1: The Hyper-industrial Epoch**（Polity；法语原 *De la misère symbolique*, t. 1, Galilée 2004） | 128 | 1 | 81 |
| Stiegler2014_Uncontrollable_Societies | "Uncontrollable Societies of Disaffected Individuals" 序言节录（Nordic Journal of Aesthetics 44–45） | 6 | 0 | 3 |
| **Stiegler2015** | **Symbolic Misery Vol. 2: The katastrophe of the sensible**（Polity；法语原 *De la misère symbolique*, t. 2, Galilée 2005） | 210 | 0 | **140** ⭐ |
| **Stiegler2020_Nanjing_Lectures_2016_2019** | **Nanjing Lectures 2016–2019**（CCC2 Irreversibility, Daniel Ross 编译） | 385 | 3 | **329** ⭐⭐⭐ |
| Stiegler2022_Une_limite_fr | "Une limite au-delà de laquelle est l'inconnu"（ELFe XX-XXI, 2022） | 6 | 0 | 6 |
| Stiegler2025_Towards_New_Industrial_Revolution | "Towards a New Industrial Revolution? Entropy and its Challenges"（Technophany 2.2, 与 Montévil/Chaix 等合著，死后出版） | 28 | 0 | 11 |

### 5 部待 OCR(v0.5 backlog)

| 文件名 | PDF 元数据推断 | 页 | 大小 |
| --- | --- | ---:| ---:|
| Stiegler1998_zh | 《技术与时间 1：爱比米修斯的过失》裴程译 | 329 | 24 MB |
| Stiegler2016 | (待人工识别) | 202 | 28 MB |
| Stiegler2017 | (待人工识别；推测 *Automatic Society Vol. 1: Future of Work*, Polity 2017) | 288 | 70 MB |
| Stiegler2021 | (待人工识别；推测遗作如 *Bifurcate* 英译或 *Nous, l'Europe* 之类) | 168 | 57 MB |
| Stiegler2022 | (待人工识别；推测另一 Polity/遗作) | 288 | 70 MB |

### 3 部元数据片段(不参与蒸馏)

| 文件 | 用途 |
| --- | --- |
| Stiegler2017_Frontmatter | 版权页 / 题献 |
| Stiegler2017_Contents | 目录页 |
| Stiegler2017_Notes_on_the_English_Translation | 译者说明 |

---

## 二、9 概念 × top-3 anchor 书

每条 = `[hits 数] book stem`。这是 SKILL.md 概念条目"证据来源"小节的主要候选。

| 概念 | rank 1 | rank 2 | rank 3 |
| --- | --- | --- | --- |
| `tertiary_retention` | 50 Nanjing | 23 2015(SymMis 2) | 15 2014(SymMis 1) |
| `epiphylogenesis` | 8 Nanjing | 7 2014(SymMis 1) | 6 2015(SymMis 2) |
| `pharmacology` | 50 2013(WMLWL) | 50 Nanjing | 1 2022_Une_limite |
| `general_organology` | 50 2015(SymMis 2) | 50 Nanjing | 26 2013(WMLWL) |
| `symbolic_misery` | 29 2014(SymMis 1) | 29 2015(SymMis 2) | 7 Nanjing |
| `proletarianization` | 43 2013(WMLWL) | 34 Nanjing | 11 2015(SymMis 2) |
| `grammatization` | 44 Nanjing | 24 2014(SymMis 1) | 20 2015(SymMis 2) |
| `disruption` | 36 Nanjing | 4 2022_Une_limite | 1 2013(WMLWL) |
| `neganthropy` | 50 Nanjing | 7 2025(Towards New Ind Rev) | 1 2013(WMLWL) |

> 观察：`Nanjing_Lectures` 在 9 概念中 8 个位列前 2，是**晚期 Stiegler 思想最完整自我陈述的英文文本**——
> 因为是面向中国研究生的系统授课，他被迫把毕生概念体系一次讲清。
> 蒸馏顺序应**以 Nanjing 为主轴**，*Symbolic Misery* 1+2 与 *What Makes Life Worth Living* 作为
> 法语原书脉络的精读补证。

---

## 三、Phase 2 蒸馏推荐阅读序

1. **`Stiegler2020_Nanjing_Lectures_2016_2019.md`**（260 KB）—— 全读，9 概念全覆盖
2. **`Stiegler2013.md`**（166 KB）—— 重点：pharmacology + proletarianization
3. **`Stiegler2015.md`**（182 KB）—— 重点：general_organology + 美学/感性政治
4. **`Stiegler2014.md`**（151 KB）—— 与 2015 配对补全 *misère symbolique* 论
5. **`Stiegler2014_Uncontrollable_Societies.md`**（17 KB）—— 6 页摘录但 symbolic_misery / proletarianization 浓度极高
6. `Stiegler2010_Le_circuit_du_désir_musical_fr.md`（60 KB）—— 法语原文风格 anchor
7. `Stiegler2022_Une_limite_fr.md`（20 KB）—— 晚期 disruption 法语 anchor
8. `Stiegler2025_Towards_New_Industrial_Revolution.md`（88 KB）—— neganthropy 死后期刊
9. `Stiegler2003_De_l_actualité_fr.md`（114 KB）—— 0 命中但内含 Stiegler 与图书馆员长对谈，性格 anchor

---

## 四、本次提取的统计上限

- `--head 30 --tail 30 --context 200 --max-hits 50` —— Phase 2 内部使用足够
- 大书(177-385pgs)中段 200+ 页未取样 —— 如需深度，可单独 `--head 999 --tail 0` 重跑某部
- CJK 概念词用子串匹配（无 `\b` 边界），可能少量误命中

---

## 五、v0.5 backlog 提醒

- **OCR pipeline**：5 部扫描 PDF（含中译《技术与时间 1》和 4 部大部头未识别 Polity/Galilée 系列）
  - 工具：`ocrmypdf --language fra+eng+chi_sim --skip-text input.pdf output.pdf`
  - 或 Acrobat Pro Paper Capture
- **OCR 后**：在 `_files/` 替换原文件，`python3 scripts/extract_pdf_evidence.py ... --force`
- **闭源补齐**：当 ANNAS 网络通时跑 `annas_acquire.py` 拿 41 部闭源原版（API key 已知）
