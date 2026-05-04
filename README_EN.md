<div align="center">

# Scholar-Wendao · 学者问道

> *Ask the way of scholars across time*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Inspired by Nuwa](https://img.shields.io/badge/Inspired%20by-nuwa.skill-orange)](https://github.com/alchaincyf/nuwa-skill)

**An open-source framework for distilling scholar perspectives into runnable analytical lenses — for humanities and social sciences researchers.**

Input a scholar's name → automatically harvest works (multilingual), secondary literature, academic debates, and biographical materials → output an analytical toolkit you can call within your research workflow.

**Not an AI chatbot. Not a roleplay toy. A scholarly analysis tool.**

[**Why?**](#why-not-just-use-nuwa) · [**Install**](#installation) · [**Usage**](#usage) · [**Architecture**](#7--1-agent-architecture) · [**Humble Epistemics**](#humble-epistemics) · [中文](README.md)

</div>

---

## Why not just use Nuwa?

[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) proved that distilling cognitive frameworks into callable skills works. Its methodology (3-fold verification, expression DNA, contradiction handling) has been validated across 13+ persona skills.

**But Nuwa's target users are entrepreneurs, product managers, and creators.** Its design carries three traits the academic context naturally rejects:

| Nuwa's design | Why academic use rejects it |
|---|---|
| First-person roleplay by default | Scholars are most allergic to turning thinkers into chatbots |
| Decision heuristics oriented toward business | Scholars don't make business decisions; they have positional shifts and public debates |
| "Expression DNA" = tonal mimicry | Translated scholars (e.g., reading Foucault in Chinese) — you'd be mimicking the translator, not the author |
| Biography stuffed into timeline | Biography matters more for scholars than entrepreneurs; needs its own chapter with strict source grading |
| Honest boundaries given a single line | Scholar distillation must directly confront Polanyi's tacit knowledge, fossilization, and other structural limits |

**Scholar-Wendao** redesigns these for humanities/social sciences:

- ✅ **Default output: third-person analytical lens** ("From Stiegler's organology perspective, the technological exteriorization logic of this phenomenon is..."), with roleplay/dialogue as opt-in
- ✅ **Concept maps** instead of "mental models", **methodological approaches** instead of "decision heuristics"
- ✅ **Multilingual primary literature acquisition** (FR/DE/EN/ZH/etc.); translations are reference only
- ✅ **Biography & character as a dedicated chapter** with **8-tier source grading** (A+ to C-)
- ✅ **Direct response to five academic critiques**: tacit knowledge, fossilization, public-vs-private, biographical rhetoric, caricaturization

A tribute, not a replacement: methodology inspired by Nuwa, but positioning, design philosophy, and target users are all independent.

---

## What it does

What humanities scholars actually need is **not "chatting with Foucault"**, but **installing Foucault's analytical lens into their research workflow** — so when reading a piece of fieldwork, they can immediately ask "what does [scholar]'s conceptual framework reveal here?"

Scholar-Wendao distills **five layers**:

| Layer | Content |
|---|---|
| **How they analyze** | Concept map — core theoretical terms used as analytical tools across ≥2 books |
| **How they enter a problem** | Methodological approaches — concrete steps when encountering type-X material |
| **Where they sit** | Academic coordinates + intellectual genealogy — school, mentors, lateral interlocutors, downstream influence |
| **How they fight** | Major debates and positional shifts — public arguments revealing real judgments |
| **How they live** | Character & conduct — separate chapter with strict source grading |

Each generated perspective skill includes the **thickest chapter**: humble epistemics — concrete declarations of five limits, reminding users **this is a tool, not a substitute**.

---

## Installation

### Install scholar-wendao itself (the meta-skill)

```bash
# To Claude's standard skill directory
git clone https://github.com/shencong/scholar-wendao.git ~/.claude/skills/scholar-wendao

# Symlink to the generic agent skill directory (compatible with other agent tools)
ln -sfn ~/.claude/skills/scholar-wendao ~/.agents/skills/scholar-wendao

# Restart Claude Desktop / Cowork to discover the new skill
```

### Recommended add-ons (for multi-source acquisition)

```bash
# Academix MCP — academic API aggregator (OpenAlex / Crossref / Semantic Scholar / arXiv)
# https://github.com/xingyulu23/Academix

# annas-mcp — Anna's Archive integration
# https://github.com/iosifache/annas-mcp
```

> Scholar-Wendao **does not reinvent acquisition wheels** — it prioritizes calling these existing MCPs and falls back to its own implementation only when they're unavailable.

---

## Usage

### Example 1 — Direct path with a scholar name

```
> Use scholar-wendao to distill Bernard Stiegler. Primary language French.
> I'm using this as an analytical lens for technology philosophy research.
```

Scholar-Wendao will:

1. **Phase 0**: Confirm Stiegler's identity (avoiding name collisions) + ask whether you have local primary materials (PDFs of original French editions)
2. **Phase 0.5**: Set up `~/.claude/skills/stiegler-perspective/` directory skeleton
3. **Phase 1**: Launch 7 parallel agents (monographs / interviews / style / secondary / debates / genealogy / archive)
4. **Phase 1.5**: Show research quality summary, wait for your confirmation
5. **Phase 2**: Extract concept map (third retention, organology, pharmakon, etc.) + methodological approaches
6. **Phase 2.5**: Show extraction summary, wait for confirmation
7. **Phase 3**: Assemble stiegler-perspective skill (default analytical lens mode)
8. **Phase 4**: 4-fold quality validation (including **caricature detection**)
9. **Phase 5**: Dual-agent refinement (including academic compliance review)

### Example 2 — Diagnostic path with only a research need

```
> I research rural education policy. I want a perspective that can see
> through the power structures behind discourse, but I don't know whose
> lens to use.
```

Scholar-Wendao will:

1. Ask 1-2 clarifying questions to locate the need (critique of educational capitalism? schools as disciplinary institutions? discourse production in education policy?)
2. Recommend 2-3 candidate scholars, each with:
   - Core lens (one sentence)
   - Why it suits you
   - School positioning
   - **Limitations** — blind spots for your specific question
   - Material accessibility
3. After you choose, enter the direct path

### Example 3 — Calling an existing perspective skill on material

After distilling Stiegler:

```
> Use stiegler-perspective to analyze this description of TikTok's
> recommendation algorithm experience: [material]
```

Output (default analytical lens mode):

> From Stiegler's three-layered organology view, this experience simultaneously involves the technical layer (the algorithm's third-retention mechanism), the psychic layer (industrialization of attention), and the social layer (its bias under capitalism).
>
> **Applying the "pharmakon" concept**: the algorithm here is both cure (satisfying immediate user preferences) and poison (depriving long-term attention taste). In *For a New Critique of Political Economy* (2009), Stiegler explicitly argues that the duality of technical objects depends on the social relations they're embedded in — meaning the analytical focus should not be the algorithm itself, but the capital-accumulation logic it serves.
>
> **Beyond Stiegler's published discussions**: he had limited engagement with short-video algorithms specifically (he passed away in 2020); the following is reasonable inference based on his conceptual system, not his stated position...

Note: default output is **third-person**, **explicitly annotates which concept is invoked**, and **distinguishes inference vs scholar's stated position**. This is the core of academic compliance.

### Example 4 — Optional opt-in dialogue mode

```
> Switch to dialogue mode. Let me discuss this with Stiegler directly.
```

When the perspective skill enters dialogue mode, the **first response must declare**:

> I am responding from Stiegler's perspective, based on reasonable inference from his published works — **not his actual views**. This dialogue may not be cited as Stiegler's real position.

And it maintains meta-awareness throughout — when encountering questions that cannot be inferred from public materials, it immediately exits character with "this is beyond my inferable range."

---

## 7 + 1 Agent Architecture

Phase 1 launches 7 parallel sub-agents:

| Agent | Task | Output |
|---|---|---|
| 1 | Core monographs and representative papers | `01-monographs.md` |
| 2 | Academic interviews and public lectures | `02-interviews.md` |
| 3 | Writing style + conceptual language | `03-style.md` |
| 4 | Secondary literature and academic debates | `04-secondary.md` |
| 5 | Positional shifts and public controversies | `05-debates.md` |
| 6 | Biography + intellectual genealogy | `06-genealogy.md` |
| **7** | **Multilingual full bibliographic archive** | **`07-archive.md`** |
| **+1 (independent chapter)** | **Character & conduct** (not an agent, but equally important) | `biography/` subdirectory |

See [`_skill-source/SKILL.md`](_skill-source/SKILL.md) for the complete workflow definition. Comparison with Nuwa's 6-agent architecture is in [`_skill-source/references/extraction-framework.md`](_skill-source/references/extraction-framework.md) §VIII.

---

## Humble Epistemics

**This is the core differentiation from other persona skills on the market** — none of them directly engage these five fundamental critiques:

### 1. Polanyi's Tacit Knowledge

> *"We always know more than we can say."* — Michael Polanyi

A scholar's **research intuition, problem-sniffing instinct, literature taste, judgment** — the "muscle memory of doing research" — is tacit and **cannot be distilled by any skill**.

→ Scholar-Wendao explicitly states: this lens only reproduces what can be made explicit. It does not replace reading the scholar's actual works.

### 2. Thought Fossilization

A scholar's thought is fluid. Foucault's early/middle/late periods differ significantly; Stiegler's late "negentropy" framework differs from his earlier "third retention" emphasis.

→ Scholar-Wendao mandates time-window labeling + evolution trajectory preservation + incremental update mechanisms.

### 3. Public vs Private

All public materials are **filtered presentations of self** — versions edited through peer review, editorial selection, and self-censorship. A scholar's private notes and intimate dialogues may contain different judgments.

→ Scholar-Wendao annotates each piece of information across an 8-tier scale (A+ to C-) marking **performance level**.

### 4. Biographical Rhetoric Contamination

Biographers have narrative preferences — they dramatize formative events, construct causal narratives, exhibit hindsight bias. "Reading philosophy in prison"-type stories get reinforced through repetition.

→ Scholar-Wendao's biography chapter mandates multi-source cross-validation + distinction between "factual layer" vs "narrative layer" — no linear causal storytelling.

### 5. Caricaturization

Over-distilled, a scholar becomes a **"signature-term-stacking machine"** — non-stop organology / non-stop pharmakon, but with no real intellectual depth. **This is the core reason academia rejects persona skills.**

→ Scholar-Wendao's Phase 4 quality validation **dedicates a caricature detection** test. FAIL means rework.

Full discussion in [`_skill-source/references/humble-epistemics.md`](_skill-source/references/humble-epistemics.md).

---

## Relationship to Similar Projects

```
nuwa-skill (general persona-distillation meta-skill)
   ├─ Methodology inspired scholar-wendao (tribute, independent design)
   └─ Generated perspective skills are compatible with the nuwa ecosystem

scholar-wendao (humanities-specific meta-skill) ← THIS PROJECT
   └─ Generates [scholar]-perspective skills
         ├─ stiegler-perspective
         ├─ foucault-perspective
         └─ ...

skill-distillery (generic skill-creation tool)
   └─ Adjacent product, different positioning (not persona-specialized)

academic-research-skills family (helps researchers do research)
   └─ Opposite direction: they help you do research,
      we help you build the tools used in research
```

**Existing scholar-class precedents** (independent projects, not generated by scholar-wendao):

- [zizek-skill](https://github.com/JikunR/zizek-skill) — Žižek
- [karlmarx-skill](https://github.com/baojiachen0214/karlmarx-skill) — Marxist methodology
- [mises-perspective](https://github.com/LijiayuDeng/mises-perspective) — Mises
- [maoxuan-skill](https://github.com/leezythu/maoxuan-skill) — Mao's methodology
- [feynman-skill](https://github.com/alchaincyf/feynman-skill) — Feynman

Scholar-Wendao doesn't aim to replace these. It provides a **unified, academically-compliant meta-tool** for future scholar distillations.

---

## Roadmap

### v0.1 · Design & methodology ✅
- [x] Design principles document
- [x] SKILL.md main workflow
- [x] 5 reference documents (including humble-epistemics core differentiation)
- [x] Prior art research
- [x] README + LICENSE

### v0.2 · Implementation 🚧
- [ ] scripts/harvest_works.py (wrapping Academix)
- [ ] scripts/download_open_access.sh
- [ ] scripts/annas_acquire.py (wrapping annas-mcp)
- [ ] scripts/biography_synth.py
- [ ] scripts/quality_check.py (with caricature detection)

### v0.3 · Validation 📋
- [ ] Distill Bernard Stiegler with scholar-wendao
- [ ] stiegler-perspective skill as the first validation example
- [ ] Cross-validation with existing Stiegler research materials

### v0.4 · Ecosystem 📋
- [ ] Distill 2-3 different types of scholars as examples (e.g., Charles Taylor / Chinese contemporary scholar / classical scholar)
- [ ] Submit to [awesome-persona-distill-skills](https://github.com/xixu-me/awesome-persona-distill-skills)
- [ ] Refine CONTRIBUTING and issue templates

### v1.0 · Academic invitation 📋
- [ ] Invite humanities scholars to use and provide feedback
- [ ] Write a paper documenting the methodology
- [ ] Explore review mechanisms by scholars themselves / school representatives

---

## Contributing

Welcome contributions:

1. **Generate new perspective skills** — distill a scholar with scholar-wendao, submit to examples/ with research data
2. **Improve methodological references** — deeper engagement with the five critiques, responses to newly identified critiques
3. **Add source strategies** — special archives for disciplines/languages you know well
4. **Improve acquisition scripts** — Academix / annas-mcp wrapper optimizations, new data source integrations
5. **Academic compliance review** — help us audit existing perspective skills for academic standards

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

- [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) — methodological inspiration
- [Academix](https://github.com/xingyulu23/Academix) — academic API aggregation
- [annas-mcp](https://github.com/iosifache/annas-mcp) — Anna's Archive integration
- [awesome-persona-distill-skills](https://github.com/xixu-me/awesome-persona-distill-skills) — persona-distillation skill ecosystem catalog
- [PersonaLLM Workshop @ NeurIPS 2025](https://personallmworkshop.github.io/) — important reference for academic discussion of LLM personas

Special thanks to the humanities and social sciences scholar community — your critical spirit is the most important external constraint keeping this skill from becoming a caricature toy.

---

## About the Author

**shencong** — Humanities and social sciences researcher at Tsinghua University

- Research areas: philosophy of technology, cultural studies, AI ethics
- Personal projects: [GitHub](https://github.com/shencong)

> *Scholar-Wendao does not replace scholars. It lends you their analytical lens.*
> *Use someone else's concept map to look at your own research material.*
> *Use someone else's methodology to ask questions you haven't asked.*
> *Not to imitate them, but to expand your own thinking — that is the real academic dialogue with scholars across time.*

---

## License

MIT License. See [LICENSE](LICENSE).

Use freely, modify freely, distribute freely. If you publicly use perspective skills generated by this tool in academic research, please cite scholar-wendao in your methodology section.

---

<div align="center">

**nuwa-skill** distilled how people think.<br>
**scholar-wendao** distills how scholars analyze.<br><br>
*Use a scholar's lens to see your own questions.*

<br>

MIT License © 2026 shencong · Inspired by [Huashu's nuwa-skill](https://github.com/alchaincyf/nuwa-skill)

</div>
