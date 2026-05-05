# Library 路径配置 · stiegler-perspective

**调研时间**:2026-05-05
**Skill 产物路径(A)**:`~/Desktop/scholar-wendao-skill/examples/stiegler-perspective/`(将通过软链分发到 `~/.claude/skills/stiegler-perspective/`)
**Library 重材料路径(B)**:用户已有的 Obsidian 数字图书馆 = `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/_files/`

## 关键决策

用户的 Obsidian Library 是**扁平化命名**(`Stiegler1998_zh.pdf`、`Stiegler2014.pdf`、`Stiegler2017.pdf`...),与 scholar-wendao 默认建议的 `works/fr/`、`works/en/`、`works/zh/` 子目录结构不同。

**不重组用户已有归档**——尊重用户既有的命名约定与跨学者扁平结构。新下载到 Library 的 Stiegler 素材沿用用户的命名规范 `Stiegler{year}[_{lang}].pdf`。

## 已有 Stiegler 一手 PDF(8 部)

| 文件名 | 著作 | 语种 | Card |
|---|---|---|---|
| Stiegler1998_zh.pdf | 《技术与时间 1:爱比米修斯的过失》 | zh(裴程译) | Stiegler1998.md |
| Stiegler2013.pdf | *What Makes Life Worth Living: On Pharmacology* | en(D. Ross 译) | Stiegler2013.md |
| Stiegler2014.pdf | *Symbolic Misery, Vol. 1: The Hyperindustrial Epoch* | en(B. Norman 译) | Stiegler2014.md |
| Stiegler2015.pdf | *States of Shock* / 待核 | en | (无 Card) |
| Stiegler2016.pdf | *Art in the Anthropocene*(中国美院讲座) | en/zh | Stiegler2016.md / Stiegler2016_zh.md |
| Stiegler2017.pdf | *Symbolic Misery, Vol. 2: The Catastrophe of the Sensible* | en | Stiegler2017.md |
| Stiegler2021.pdf | *Symbolic Misery, Vol. 1*(2nd ed.) | en | Stiegler2021.md |
| Stiegler2022.pdf | *Symbolic Misery, Vol. 2*(2nd ed.) | en | Stiegler2022.md |

## 通过 OpenAlex/Crossref 采集到的元数据(Phase 1 Agent 7)

- 总数:395 部(filter 后:fr 136 + en 139 + und 120)
- OA 覆盖率:10%(开放获取 42 部 / 闭源 353 部)
- OpenAlex Author ID:`A5055549487`
- 详细:`07-archive.md` / `07-archive.json`

## 待获取(Phase 1 闭源清单——未实际下载,仅清单)

由于用户未配置 `ANNAS_API_KEY`,采用清单模式。优先级:法语原版 > 英译 > 中译。

**关键缺口**(法语原版):
- *La technique et le temps, 1: La faute d'Épiméthée*(Galilée, 1994)
- *La technique et le temps, 2: La désorientation*(Galilée, 1996)
- *La technique et le temps, 3: Le temps du cinéma...*(Galilée, 2001)
- *De la misère symbolique, Tomes 1 & 2*(Galilée, 2004 & 2005)
- *Mécréance et discrédit*(三卷,Galilée, 2004-2006)
- *Pour une nouvelle critique de l'économie politique*(Galilée, 2009)
- *Passer à l'acte*(Galilée, 2003)— 自传(prison memoir)
- *Échographies de la télévision*(与 Derrida 合著, Galilée, 1996)
- *Qu'appelle-t-on panser?*(2 vols., Les Liens qui Libèrent, 2018-2020)
- *Bifurquer: il n'y a pas d'alternative*(Les Liens qui Libèrent, 2020)— 集体作品

**英译关键缺口**:
- *Technics and Time*(三卷, Stanford UP)
- *Acting Out*(Stanford UP, 2009 — Passer à l'acte 英译)
- *States of Shock: Stupidity and Knowledge in the 21st Century*(Polity, 2015)
- *Automatic Society, Vol. 1: The Future of Work*(Polity, 2017)
- *The Age of Disruption: Technology and Madness in Computational Capitalism*(Polity, 2019)
- *The Neganthropocene*(Open Humanities Press, 2018, OA — 应可下载)

## 信息源黑名单(strict)

- ❌ 知乎、微信公众号、百度百科、抖音、小红书
- ✅ HAL、Persée、Cairn、BnF Gallica、INA(视频)、JSTOR、PhilPapers、Polity 出版社官页、Stanford UP、Stanford Encyclopedia of Philosophy、ArsIndustrialis 协会档案、IRI、Goldsmiths 讲座频道、Open Humanities Press(OA)、CNKI、商务印书馆、南京大学出版社、译林出版社、重庆大学出版社拜德雅、华东师大出版社
