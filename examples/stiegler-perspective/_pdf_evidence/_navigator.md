# `_pdf_evidence/` Navigator · 自动生成

> 由 `scripts/regenerate_navigator.py` 从 `_index.json` 自动生成（2026-05-05）。
> 本目录是 Workflow B 蒸馏的**强制证据库**——SKILL.md 每个核心概念的定义、引文、风格判断
> 都必须能追溯到这里某一份 `{book}.md` 的某一页。

## 一、PDF 评估总览（共 19 部）

- 可机读主要来源(≥10 页 + 有概念命中):**11 部** · 总 960,408 字符 · 总 1223 concept hits
- 元数据片段(目录/序言/版权页):3 部
- 待 OCR(扫描无文字层):5 部 · v0.5 OCR backlog

### 可机读主要来源(11 部)

| 文件 | 页 | empty | chars | total hits |
| --- | ---: | ---: | ---: | ---: |
| Stiegler2018_The_Neganthropocene_en | 349 | 3 | 118,585 | **336** |
| Stiegler2020_Nanjing_Lectures_2016_2019 | 385 | 3 | 115,611 | **329** |
| Stiegler2013 | 177 | 2 | 102,587 | **156** |
| Stiegler2021_Bifurcate_en | 330 | 4 | 121,252 | **144** |
| Stiegler2015 | 210 | 0 | 119,019 | **140** |
| Stiegler2014 | 128 | 1 | 116,674 | **81** |
| Stiegler2010_Le_circuit_du_d_sir_musical_fr | 17 | 0 | 49,300 | **17** |
| Stiegler2025_Towards_a_New_Industrial_Revolution_Entr | 28 | 0 | 81,048 | **11** |
| Stiegler2022_Une_limite_au_del_de_laquelle_est_l_inco_fr | 6 | 0 | 14,924 | **6** |
| Stiegler2014_Uncontrollable_Societies_of_Disaffected | 6 | 0 | 14,546 | **3** |
| Stiegler2003_De_l_actualit_la_m_moire_de_l_actualit_fr | 38 | 0 | 106,862 | **0** |

### 元数据片段(3 部 · 不参与蒸馏)

- `Stiegler2017_Contents` (1 页)
- `Stiegler2017_Frontmatter` (4 页)
- `Stiegler2017_Notes_on_the_English_Translation` (3 页)

### 待 OCR(5 部 · v0.5 backlog)

- `Stiegler1998_zh` (329 页 · empty=60)
- `Stiegler2016` (202 页 · empty=60)
- `Stiegler2017` (288 页 · empty=60)
- `Stiegler2021` (168 页 · empty=60)
- `Stiegler2022` (288 页 · empty=60)

**OCR 命令**:
```
brew install ocrmypdf  # 一次性
ocrmypdf --language fra+eng+chi_sim --skip-text input.pdf input.pdf
# OCR 完后重跑:
python3 scripts/extract_pdf_evidence.py --filter "<filename>.pdf" --force ...
```

## 二、概念 × top-3 anchor 矩阵

每条 = `[hits 数] book stem`。**Workflow B Phase 2.1** 强制概念条目的「证据来源」小节链接 top-3 anchor。

| 概念 | rank 1 | rank 2 | rank 3 | 全库总 |
| --- | --- | --- | --- | ---: |
| `tertiary_retention` | 50 Stiegler2018_The_Neganthropoce | 50 Stiegler2020_Nanjing_Lectures_ | 23 Stiegler2015 | 156 |
| `epiphylogenesis` | 9 Stiegler2018_The_Neganthropoce | 8 Stiegler2020_Nanjing_Lectures_ | 7 Stiegler2014 | 37 |
| `pharmacology` | 50 Stiegler2013 | 50 Stiegler2018_The_Neganthropoce | 50 Stiegler2020_Nanjing_Lectures_ | 174 |
| `general_organology` | 50 Stiegler2015 | 50 Stiegler2018_The_Neganthropoce | 50 Stiegler2020_Nanjing_Lectures_ | 198 |
| `symbolic_misery` | 29 Stiegler2014 | 29 Stiegler2015 | 7 Stiegler2018_The_Neganthropoce | 81 |
| `proletarianization` | 43 Stiegler2013 | 37 Stiegler2018_The_Neganthropoce | 34 Stiegler2020_Nanjing_Lectures_ | 155 |
| `grammatization` | 44 Stiegler2020_Nanjing_Lectures_ | 33 Stiegler2018_The_Neganthropoce | 24 Stiegler2014 | 143 |
| `disruption` | 50 Stiegler2018_The_Neganthropoce | 36 Stiegler2020_Nanjing_Lectures_ | 28 Stiegler2021_Bifurcate_en | 120 |
| `neganthropy` | 50 Stiegler2018_The_Neganthropoce | 50 Stiegler2020_Nanjing_Lectures_ | 50 Stiegler2021_Bifurcate_en | 159 |

## 三、Workflow B 蒸馏推荐阅读序(按命中数降序)

1. **`Stiegler2018_The_Neganthropocene_en.md`** (349 页 / 118.6K 字 / 336 hits)
2. **`Stiegler2020_Nanjing_Lectures_2016_2019.md`** (385 页 / 115.6K 字 / 329 hits)
3. **`Stiegler2013.md`** (177 页 / 102.6K 字 / 156 hits)
4. **`Stiegler2021_Bifurcate_en.md`** (330 页 / 121.3K 字 / 144 hits)
5. **`Stiegler2015.md`** (210 页 / 119.0K 字 / 140 hits)
6. **`Stiegler2014.md`** (128 页 / 116.7K 字 / 81 hits)
7. **`Stiegler2010_Le_circuit_du_d_sir_musical_fr.md`** (17 页 / 49.3K 字 / 17 hits)
8. **`Stiegler2025_Towards_a_New_Industrial_Revolution_Entr.md`** (28 页 / 81.0K 字 / 11 hits)
9. **`Stiegler2022_Une_limite_au_del_de_laquelle_est_l_inco_fr.md`** (6 页 / 14.9K 字 / 6 hits)
10. **`Stiegler2014_Uncontrollable_Societies_of_Disaffected.md`** (6 页 / 14.5K 字 / 3 hits)

## 四、本次提取的统计上限

- `--head 30 --tail 30 --context 200 --max-hits 50`(extract_pdf_evidence.py 默认)
- 大书中段(p.30+ 到 p.last-30)未取样;如需深度,单独 `--head 999 --tail 0` 重跑某部
- CJK 概念词用子串匹配(无 `\b` 边界),可能少量误命中
