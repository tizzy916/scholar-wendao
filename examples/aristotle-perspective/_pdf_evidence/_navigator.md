# `_pdf_evidence/` Navigator · 自动生成

> 由 `scripts/regenerate_navigator.py` 从 `_index.json` 自动生成（2026-05-05）。
> 本目录是 Workflow B 蒸馏的**强制证据库**——SKILL.md 每个核心概念的定义、引文、风格判断
> 都必须能追溯到这里某一份 `{book}.md` 的某一页。

## 一、PDF 评估总览（共 5 部）

- 可机读主要来源(≥10 页 + 有概念命中):**5 部** · 总 659,585 字符 · 总 2638 concept hits
- 元数据片段(目录/序言/版权页):0 部
- 待 OCR(扫描无文字层):0 部 · v0.5 OCR backlog

### 可机读主要来源(5 部)

| 文件 | 页 | empty | chars | total hits |
| --- | ---: | ---: | ---: | ---: |
| Aristotle_-322_Organon_en | 3354 | 0 | 109,088 | **666** |
| Aquinas_1273_Commentary_on_Metaphysics_Vol_I_en | 501 | 0 | 169,417 | **579** |
| Aristotle_-322_Nicomachean_Ethics_en | 274 | 0 | 152,199 | **489** |
| Aristotle_-322_Politics_en | 287 | 1 | 154,250 | **459** |
| Aristotle_-322_De_Anima_en | 430 | 6 | 74,631 | **445** |

## 二、概念 × top-3 anchor 矩阵

每条 = `[hits 数] book stem`。**Workflow B Phase 2.1** 强制概念条目的「证据来源」小节链接 top-3 anchor。

| 概念 | rank 1 | rank 2 | rank 3 | 全库总 |
| --- | --- | --- | --- | ---: |
| `form_matter` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 250 |
| `physis` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 250 |
| `praxis_poiesis_theoria` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 250 |
| `telos` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 250 |
| `mean_doctrine` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 250 |
| `psyche` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 232 |
| `potentiality_actuality` | 50 Aristotle_-322_De_Anima_en | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 231 |
| `virtue` | 50 Aristotle_-322_Nicomachean_Eth | 50 Aristotle_-322_Organon_en | 50 Aristotle_-322_Politics_en | 213 |
| `ousia` | 50 Aristotle_-322_Organon_en | 50 Aquinas_1273_Commentary_on_Met | 29 Aristotle_-322_De_Anima_en | 135 |
| `eudaimonia` | 50 Aristotle_-322_Organon_en | 37 Aristotle_-322_Nicomachean_Eth | 18 Aristotle_-322_Politics_en | 117 |
| `four_causes` | 50 Aristotle_-322_Organon_en | 50 Aquinas_1273_Commentary_on_Met | 9 Aristotle_-322_De_Anima_en | 110 |
| `categories` | 50 Aristotle_-322_Organon_en | 45 Aquinas_1273_Commentary_on_Met | 6 Aristotle_-322_De_Anima_en | 106 |
| `phronesis` | 42 Aristotle_-322_Organon_en | 35 Aristotle_-322_Nicomachean_Eth | 13 Aristotle_-322_Politics_en | 101 |
| `polis_politike` | 50 Aristotle_-322_Politics_en | 12 Aristotle_-322_Nicomachean_Eth | 11 Aristotle_-322_Organon_en | 73 |
| `first_philosophy` | 43 Aquinas_1273_Commentary_on_Met | 13 Aristotle_-322_Organon_en | 7 Aristotle_-322_Politics_en | 70 |

## 三、Workflow B 蒸馏推荐阅读序(按命中数降序)

1. **`Aristotle_-322_Organon_en.md`** (3354 页 / 109.1K 字 / 666 hits)
2. **`Aquinas_1273_Commentary_on_Metaphysics_Vol_I_en.md`** (501 页 / 169.4K 字 / 579 hits)
3. **`Aristotle_-322_Nicomachean_Ethics_en.md`** (274 页 / 152.2K 字 / 489 hits)
4. **`Aristotle_-322_Politics_en.md`** (287 页 / 154.2K 字 / 459 hits)
5. **`Aristotle_-322_De_Anima_en.md`** (430 页 / 74.6K 字 / 445 hits)

## 四、本次提取的统计上限

- `--head 30 --tail 30 --context 200 --max-hits 50`(extract_pdf_evidence.py 默认)
- 大书中段(p.30+ 到 p.last-30)未取样;如需深度,单独 `--head 999 --tail 0` 重跑某部
- CJK 概念词用子串匹配(无 `\b` 边界),可能少量误命中
