#!/usr/bin/env python3
"""
quality_check.py · Phase 4 质量验证（v0.4 含 6 项静态检查 + 漫画化 + 引文核验 + bracketing）

为 scholar-wendao 的 Phase 4 服务：检查生成的 [scholar]-perspective skill
是否符合学术合规要求。

测试项（v0.4）：
  4.1 已知测试（Sanity Check）—— 由 agent 执行
  4.2 边缘测试（Edge Case）—— 由 agent 执行
  4.3 漫画化检测（Caricature Test）⭐ 学者问道独有
  4.4 默会知识声明检查（六项·v0.4 新增第六项「死亡-尊重边界」）—— 静态检查
  4.5 引文 page-anchor 强制核验（v0.4 新增）—— 静态检查 + 读 _pdf_evidence
  4.6 Narrative-bracketing 自动检测（v0.4 新增）—— 静态检查
  4.7 通过标准评分

设计：
  4.1/4.2/4.3 需要让独立 agent 用新生成的 skill 跑测试，所以本脚本
  生成"测试任务"prompt，agent 执行后把回答存到指定文件，本脚本
  读取并分析（启发式 + 模式匹配）。

  4.4/4.5/4.6/4.7 是纯静态检查，不需要 LLM。

用法：
  # 仅静态检查
  python3 quality_check.py --skill SKILL.md \\
    [--evidence-dir _pdf_evidence]   # v0.4：传入则启用引文核验

  # 生成测试任务
  python3 quality_check.py --prepare --skill SKILL.md --scholar "Bernard Stiegler"

  # 完整分析（含 agent 测试回答）
  python3 quality_check.py --analyze \\
    --skill SKILL.md --responses _quality_test_responses/

许可：MIT
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ===========================================================
# 静态检查：6 项必备声明 + 通过标准（v0.4）
# ===========================================================

REQUIRED_DECLARATIONS = {
    "polanyi": [r"波兰尼", r"默会", r"tacit\s+knowledge", r"Polanyi"],
    "fossilization": [r"化石化", r"调研时间", r"采集.*?截至", r"snapshot"],
    "public_vs_private": [r"公开.*?(私下|表演|展演)", r"前台", r"展演自我", r"performance"],
    "biographical_rhetoric": [r"传记修辞", r"叙事建构", r"narrative\s+construction"],
    "caricature": [r"漫画化", r"caricature", r"口头禅"],
    # v0.4 P5 #13 新增：死亡-尊重边界（自杀 / 监禁 / 重大创伤事件的特别约束）
    "death_respect_boundary": [
        r"死亡.*?边界", r"自杀.*?(尊严|尊重|节制|戏剧化)",
        r"creative\s+disclaimer", r"narrative-bracket",
        r"不戏剧化", r"不连接因果", r"创伤.*?(尊重|节制)",
    ],
}

# Phase 4 通过标准（v0.4 含新增项）
THRESHOLDS = {
    "concept_count_min": 3,
    "concept_count_max": 7,
    "heuristic_count_min": 5,
    "primary_source_ratio_min": 0.5,
    "biography_grade_required": True,
    "six_declarations_required": True,  # v0.4 从 5 升 6
    "citation_anchor_min_pass_rate": 0.8,  # v0.4：≥80% 引文页码可证
}


def static_check(skill_path: Path, evidence_dir: Path | None = None) -> dict[str, Any]:
    text = skill_path.read_text(encoding="utf-8")
    results: dict[str, Any] = {
        "skill_path": str(skill_path),
        "checked_at": datetime.now().isoformat(),
        "checks": {},
        "score": 0,
        "issues": [],
    }

    # 1. 六大批评声明（v0.4：从 5 升 6）
    declarations = {}
    for key, patterns in REQUIRED_DECLARATIONS.items():
        present = any(re.search(pat, text, re.IGNORECASE) for pat in patterns)
        declarations[key] = present
        if not present:
            results["issues"].append(f"缺失诚实边界声明：{key}（任一关键词都未出现）")
    results["checks"]["six_declarations"] = declarations
    results["checks"]["six_declarations_pass"] = all(declarations.values())

    # 2. 概念地图数量
    concept_blocks = re.findall(r"###\s+(?:核心)?概念\s*\d+[：:]", text)
    if not concept_blocks:
        # 备用模式
        concept_blocks = re.findall(r"###\s+模型\s*\d+[：:]", text)
    cc = len(concept_blocks)
    in_range = THRESHOLDS["concept_count_min"] <= cc <= THRESHOLDS["concept_count_max"]
    results["checks"]["concept_count"] = cc
    results["checks"]["concept_count_pass"] = in_range
    if not in_range:
        results["issues"].append(
            f"概念数量 {cc} 不在 [{THRESHOLDS['concept_count_min']}, "
            f"{THRESHOLDS['concept_count_max']}] 范围内"
        )

    # 3. 方法论进路数量
    heuristic_blocks = re.findall(r"###\s+(?:进路|启发式|方法论进路)\s*\d+[：:]", text)
    hc = len(heuristic_blocks)
    h_ok = hc >= THRESHOLDS["heuristic_count_min"]
    results["checks"]["heuristic_count"] = hc
    results["checks"]["heuristic_count_pass"] = h_ok
    if not h_ok:
        results["issues"].append(f"方法论进路数 {hc} 少于 {THRESHOLDS['heuristic_count_min']}")

    # 4. 调研时间（v0.4 P4 #11 修复：粗体 / 空格 / 中英冒号都要 robust）
    # 之前 r"调研时间[：:]\s*\d{4}" 在用户写 **调研时间**：2026 时失效（粗体打断 regex）
    has_research_date = bool(re.search(r"调研时间[*\s]*[:：][*\s]*\d{4}", text))
    results["checks"]["has_research_date"] = has_research_date
    if not has_research_date:
        results["issues"].append("未声明调研时间（化石化警示要求）")

    # 5. 默认分析镜片模式（不是默认扮演）
    default_lens_mode = bool(re.search(r"默认.*?分析镜片|默认.*?第三人称", text))
    has_optin_dialogue = bool(re.search(r"opt-in|对话模式.*?可选|主动.*?(切换|激活).*?(对话|扮演)", text))
    results["checks"]["default_lens_mode"] = default_lens_mode
    results["checks"]["has_optin_dialogue"] = has_optin_dialogue
    if not default_lens_mode:
        results["issues"].append("未明确'默认分析镜片模式'——可能是漫画化风险源")
    if not has_optin_dialogue:
        results["issues"].append("未明确对话模式为 opt-in")

    # 6. 一手来源占比（基于来源摘要章节）
    one_match = re.search(r"一手来源[（(].*?[)）]", text)
    a_grade_count = len(re.findall(r"\bA\+?\b|A 级", text))
    c_grade_count = len(re.findall(r"\bC[+\-]?\b|C 级", text))
    if a_grade_count + c_grade_count > 0:
        primary_ratio = a_grade_count / (a_grade_count + c_grade_count)
        results["checks"]["primary_ratio"] = round(primary_ratio, 2)
        if primary_ratio < THRESHOLDS["primary_source_ratio_min"]:
            results["issues"].append(
                f"一手来源占比 {primary_ratio:.0%} 低于 {THRESHOLDS['primary_source_ratio_min']:.0%}"
            )
    else:
        results["checks"]["primary_ratio"] = None
        results["issues"].append("无法估算一手/二手来源占比（缺少 A/C 等级标注）")

    # 7. v0.4 新增：引文 page-anchor 核验（仅在 evidence_dir 提供时执行）
    citation_check = check_citation_anchors(text, evidence_dir) if evidence_dir else None
    if citation_check is not None:
        results["checks"]["citation_anchor"] = citation_check
        if not citation_check["pass"]:
            for unverified in citation_check["unverified"][:5]:  # 前 5 条
                results["issues"].append(
                    f"引文不可定位: '{unverified['quote'][:50]}...' "
                    f"标 {unverified['source']} p.{unverified['page']}，"
                    f"但 {unverified['evidence_md']} 该页无此文本"
                )

    # 8. v0.4 新增：narrative-bracketing 检测
    bracketing = check_narrative_bracketing(text)
    results["checks"]["narrative_bracketing"] = bracketing
    if not bracketing["pass"] and bracketing["formative_events_total"] > 0:
        results["issues"].append(
            f"narrative-bracketing：{bracketing['formative_events_total']} 个形成性事件中，"
            f"{bracketing['without_bracketing']} 个缺事实层/叙事层双标注"
        )

    # 计算总分（v0.4 重排：六大声明 25 + 概念 15 + 进路 15 + 调研日期 5 + 模式 10 + 一手 10 + 引文 10 + bracketing 10）
    score = 0
    if results["checks"]["six_declarations_pass"]:
        score += 25
    if results["checks"]["concept_count_pass"]:
        score += 15
    if results["checks"]["heuristic_count_pass"]:
        score += 15
    if has_research_date:
        score += 5
    if default_lens_mode and has_optin_dialogue:
        score += 10
    pr = results["checks"].get("primary_ratio")
    if pr is not None and pr >= THRESHOLDS["primary_source_ratio_min"]:
        score += 10
    if citation_check is None:
        # 没启用 evidence 校验：补满 10 分（向后兼容）
        score += 10
    elif citation_check["pass"]:
        score += 10
    if bracketing["pass"]:
        score += 10

    results["score"] = score
    results["pass"] = score >= 80 and not any(
        issue.startswith("缺失诚实边界") for issue in results["issues"]
    )

    return results


# ===========================================================
# v0.4 新增检查器
# ===========================================================

def _slug(name: str) -> str:
    """文件名归一化，匹配 _pdf_evidence/{slug}.md。"""
    return re.sub(r"\W+", "", (name or "").lower())


# 引文模式：匹配 "...书名/缩写, 20XX, p. NNN" 或 "in {Book} (year), p. NN"
# 一个引文 = 一对 quote 文本 + source 标识 + page。
# 我们用启发式扫所有 quote 块（> ... > —— ...）后跟 page 标记。
CITATION_PATTERNS = [
    # 形如  > "..." \n > —— *Book Title*, year, p. 19
    re.compile(
        r'>\s*["“"](?P<quote>[^"”"]{20,}?)["""]\s*\n\s*>\s*(?:——|--)\s*[^,\n]*?'
        r'(?P<source>(?:\*[^*]+\*|《[^》]+》|[A-Z][A-Za-z\s,:]+)),?\s*'
        r'(?:[A-Z][a-z]+\s*(?:UP|Press|Polity|Galilée|Flammarion)?,?\s*)?'
        r'(?:\d{4},?\s*)?'
        r'(?:pp?\.|页)\s*(?P<page>\d+)',
        re.MULTILINE
    ),
]


def _extract_citations(text: str) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for pat in CITATION_PATTERNS:
        for m in pat.finditer(text):
            citations.append({
                "quote": m.group("quote").strip(),
                "source": m.group("source").strip().strip("*").strip("《》"),
                "page": int(m.group("page")),
            })
    return citations


def check_citation_anchors(skill_text: str, evidence_dir: Path) -> dict[str, Any]:
    """v0.4 P0 #2：每条引文必须能在 _pdf_evidence/{book}.md 的 p.{N} 段中搜到。"""
    citations = _extract_citations(skill_text)

    if not citations:
        return {
            "pass": True,
            "total": 0,
            "verified": 0,
            "unverified": [],
            "note": "no citations with page anchors detected"
        }

    if not evidence_dir.exists():
        return {
            "pass": False,
            "total": len(citations),
            "verified": 0,
            "unverified": [{"quote": c["quote"], "source": c["source"],
                            "page": c["page"], "evidence_md": "(missing dir)"}
                           for c in citations],
            "note": f"evidence dir {evidence_dir} does not exist"
        }

    evidence_files = [f for f in evidence_dir.glob("*.md") if not f.name.startswith("_")]
    unverified: list[dict[str, Any]] = []
    verified = 0
    verified_via_fulltext = 0  # v0.4：page-anchor 不命中但全文搜到的回退验证

    def _normalize(s: str) -> str:
        # v0.4：删除标点 + 删除全部空白（处理 OCR 断行造成的"phar macology"等切碎）
        # 这样允许 OCR-corrupted evidence 与干净引文做 substring 匹配
        return re.sub(r"[\W_]+", "", s.lower())

    # 预先 normalize 全部 evidence 文本作为 fulltext fallback
    fulltext_normalized: dict[str, str] = {}
    for ef in evidence_files:
        try:
            fulltext_normalized[ef.name] = _normalize(ef.read_text(encoding="utf-8"))
        except Exception:
            pass

    def _fulltext_search(quote: str) -> str | None:
        """返回首个含 quote 60-字 子串的 evidence 文件名，否则 None。"""
        for cand in [quote[:60], quote[-60:] if len(quote) > 60 else "",
                     quote[len(quote) // 2 - 30: len(quote) // 2 + 30] if len(quote) > 80 else ""]:
            if not cand:
                continue
            n = _normalize(cand)
            if not n:
                continue
            for fname, fulltext in fulltext_normalized.items():
                if n in fulltext:
                    return fname
        return None

    def _source_tokens(source: str) -> list[str]:
        """从 source 字串提取 ≥4 字符的有意义 token（忽略 stop words）。"""
        stop = {"the", "and", "for", "with", "vol", "volume", "what", "from", "into",
                "this", "that", "des", "les", "une", "tome", "epoch", "press",
                "polity", "stanford", "university"}
        toks = re.findall(r"[A-Za-z一-鿿]{4,}", source.lower())
        return [t for t in toks if t not in stop]

    for c in citations:
        # 找最匹配的 evidence file（按 source token 与文件名子串重合）
        src_tokens = _source_tokens(c["source"])
        best_match: Path | None = None
        best_score = 0
        for f in evidence_files:
            if f.name.startswith("_"):
                continue  # 跳过 _index.json _navigator.md _concepts.json
            f_slug = _slug(f.stem)
            # 计分：每个 src_token 是否在 f_slug 中作为子串出现
            hits = sum(1 for t in src_tokens if t in f_slug)
            if hits > best_score:
                best_score = hits
                best_match = f

        # 至少 1 个 token 重合（多数情况 source 含年份 / 关键词，大多数都能命中）
        if not best_match or best_score < 1:
            # v0.4 fallback：全文搜 evidence
            ft_hit = _fulltext_search(c["quote"])
            if ft_hit:
                verified += 1
                verified_via_fulltext += 1
                continue
            unverified.append({
                "quote": c["quote"],
                "source": c["source"],
                "page": c["page"],
                "evidence_md": "(no match)",
            })
            continue

        ev_text = best_match.read_text(encoding="utf-8")

        # v0.4 修：evidence 里 page anchor 有两种格式：
        #   "### p.{N}\n" （head/tail 段，逐页 dump）
        #   "- **p.{N}** [`...`]: …" （concept_hits 段，单行片段）
        page = c["page"]
        page_text = ""
        # 优先 head/tail 全页
        m1 = re.search(rf"### p\.{page}\s*\n", ev_text)
        if m1:
            # 取到下一个 ### 标题前
            tail = ev_text[m1.end():]
            next_h = re.search(r"\n### ", tail)
            page_text = tail[: next_h.start() if next_h else 3500]
        # 同时也吸收 concept_hits 里指向同页的所有片段
        for m2 in re.finditer(rf"-\s*\*\*p\.{page}\*\*[^\n]*", ev_text):
            page_text += "\n" + m2.group(0)

        if not page_text.strip():
            # v0.4 fallback：page anchor 不存在 → 全文搜
            ft_hit = _fulltext_search(c["quote"])
            if ft_hit:
                verified += 1
                verified_via_fulltext += 1
                continue
            unverified.append({
                "quote": c["quote"],
                "source": c["source"],
                "page": c["page"],
                "evidence_md": str(best_match.name),
            })
            continue

        # 用引文中最长的连续片段（前 60 字 / 中间 60 字 / 后 60 字 任一命中即可）
        quote = c["quote"]
        candidates = [
            quote[:60],
            quote[len(quote) // 2 - 30: len(quote) // 2 + 30] if len(quote) > 60 else "",
            quote[-60:] if len(quote) > 60 else "",
        ]
        page_norm = _normalize(page_text)
        hit = any(_normalize(cand) in page_norm for cand in candidates if cand)

        if hit:
            verified += 1
        else:
            # v0.4 fallback：page-anchor 不命中 → 扫全部 evidence 全文
            ft_hit = _fulltext_search(c["quote"])
            if ft_hit:
                verified += 1
                verified_via_fulltext += 1
            else:
                unverified.append({
                    "quote": c["quote"],
                    "source": c["source"],
                    "page": c["page"],
                    "evidence_md": str(best_match.name),
                })

    pass_rate = verified / len(citations) if citations else 1.0
    return {
        "pass": pass_rate >= THRESHOLDS["citation_anchor_min_pass_rate"],
        "total": len(citations),
        "verified": verified,
        "verified_via_fulltext": verified_via_fulltext,
        "pass_rate": round(pass_rate, 2),
        "unverified": unverified,
    }


def check_narrative_bracketing(skill_text: str) -> dict[str, Any]:
    """v0.4 P1 #4：人格章节中"形成性事件"段落必须含事实层 + 叙事层。"""
    # 找"人格"或"形成性事件"或"生平"章节
    section_match = re.search(
        r"##\s*[^\n]*?(?:人格与处世|生平|formative|biograph|监狱|入狱)[^\n]*\n([\s\S]+?)(?=\n## |\Z)",
        skill_text,
        re.IGNORECASE
    )
    if not section_match:
        return {
            "pass": True,
            "formative_events_total": 0,
            "without_bracketing": 0,
            "note": "no biographical section found"
        }

    section = section_match.group(1)
    # 启发式：每个独立"事件"段落 = 含 4 位数年份 + 至少 1 个动词性事件描述
    event_blocks = re.findall(
        r"(\d{4}[—\-–\s]*?\d{0,4}[年]?[^\n]{20,400})",
        section
    )
    if not event_blocks:
        return {
            "pass": True,
            "formative_events_total": 0,
            "without_bracketing": 0,
            "note": "no formative events with year detected"
        }

    fact_pattern = re.compile(r"事实层|fact-level|来源等级|A\+?|B\+?|C\+?", re.IGNORECASE)
    narr_pattern = re.compile(r"叙事层|narrative-level|学者自述|传记修辞|self-narrative|戏剧化", re.IGNORECASE)

    without_bracketing = 0
    for block in event_blocks:
        # 在事件段周围 ±200 字范围找标注
        idx = section.find(block)
        ctx = section[max(0, idx - 200): idx + len(block) + 400]
        has_fact = bool(fact_pattern.search(ctx))
        has_narr = bool(narr_pattern.search(ctx))
        if not (has_fact and has_narr):
            without_bracketing += 1

    return {
        "pass": without_bracketing == 0,
        "formative_events_total": len(event_blocks),
        "without_bracketing": without_bracketing,
    }


# ===========================================================
# 测试任务生成（4.1 / 4.2 / 4.3）
# ===========================================================

CARICATURE_TEST_PROMPT = """\
# Phase 4.3 漫画化检测任务

> 用 {skill_name} 分析以下日常材料，**不允许**调用任何外部知识：

## 测试材料

{material}

## 你的任务

用 {scholar} 的概念地图和方法论进路，对上述材料进行学术分析。

## 严格约束

- 必须显式调用 ≥1 个核心概念
- 每次调用必须给出具体分析，**不是贴标签**
- 至少包含一处该学者公开材料里**没有直接说过**但合理推断的观点
- 整段读起来必须像学术评注，**不像段子合集**

完成后回答以下自检：

1. 我使用了哪些核心概念？分别用了几次？
2. 我的分析是真的在拓展材料的理解，还是在复读学者的口头禅？
3. 如果删除学者名字，这段分析仍然有学术深度吗？

回答存到：`_quality_test_responses/caricature_test.md`
"""

KNOWN_TEST_PROMPT = """\
# Phase 4.1 已知测试任务

> 用 {skill_name} 回答以下 3 个 {scholar} **公开表态过**的问题。

回答完毕后，{scholar} 实际立场会与你回答对照——方向必须一致。

## 问题（请逐一回答）

1. {q1}

2. {q2}

3. {q3}

存到：`_quality_test_responses/known_test.md`
"""

EDGE_TEST_PROMPT = """\
# Phase 4.2 边缘测试任务

> 用 {skill_name} 回答 1 个 {scholar} 没公开讨论过但相关的问题。

期望：你应该明确说"基于其概念体系的合理推断"，不应该斩钉截铁。

## 问题

{question}

存到：`_quality_test_responses/edge_test.md`
"""


def prepare_tests(skill_path: Path, scholar: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_path.parent.name

    # 漫画化测试材料示例（实际使用时 agent 应自动生成或用户提供）
    caricature_material = (
        "[Phase 4.3 测试材料 placeholder] 请把一段日常材料（如新闻报道、"
        "社交媒体帖子、产品页面）粘贴到此处，长度 200-500 字。"
    )

    (output_dir / "_caricature_task.md").write_text(
        CARICATURE_TEST_PROMPT.format(
            skill_name=skill_name, scholar=scholar, material=caricature_material
        ),
        encoding="utf-8",
    )

    (output_dir / "_known_test_task.md").write_text(
        KNOWN_TEST_PROMPT.format(
            skill_name=skill_name,
            scholar=scholar,
            q1=f"[人工填写：{scholar} 公开表态过的议题 1]",
            q2=f"[人工填写：{scholar} 公开表态过的议题 2]",
            q3=f"[人工填写：{scholar} 公开表态过的议题 3]",
        ),
        encoding="utf-8",
    )

    (output_dir / "_edge_test_task.md").write_text(
        EDGE_TEST_PROMPT.format(
            skill_name=skill_name,
            scholar=scholar,
            question=f"[人工填写：{scholar} 没公开讨论过但相关的议题]",
        ),
        encoding="utf-8",
    )

    print(f"✓ 三份测试任务已生成到：{output_dir}", file=sys.stderr)
    print(f"  - _caricature_task.md（漫画化检测）", file=sys.stderr)
    print(f"  - _known_test_task.md（已知测试）", file=sys.stderr)
    print(f"  - _edge_test_task.md（边缘测试）", file=sys.stderr)
    print(f"\n下一步：让 agent 读取每份任务并把回答存到 {output_dir}/")
    print(f"完成后用 --analyze 验证。", file=sys.stderr)


# ===========================================================
# 测试结果分析
# ===========================================================

def analyze_caricature(response_path: Path) -> dict[str, Any]:
    """启发式判断回答是否漫画化。"""
    if not response_path.exists():
        return {"ok": False, "reason": "回答文件不存在", "score": 0}

    text = response_path.read_text(encoding="utf-8")
    word_count = len(text.split())
    if word_count < 100:
        return {"ok": False, "reason": "回答过短，无法判断", "score": 0}

    # 检测：术语堆砌密度
    # 取最常见的 5 个连字符术语 + 全大写或首字母大写的概念词
    technical_terms = re.findall(r"\b[a-zA-Z]{5,}-?[a-zA-Z]{4,}\b|\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b", text)
    term_density = len(technical_terms) / max(word_count, 1) * 100  # 每 100 字术语数

    # 检测：是否有"必要的不确定"声明（合理推断/超出范围）
    has_uncertainty = bool(re.search(
        r"基于.*?推断|可能|或许|不确定|超出.*?范围|没有公开讨论",
        text
    ))

    # 检测：是否有具体引用/案例
    has_citations = bool(re.search(r"在《.*?》|p\.\s*\d+|\d{4}.*?年", text))

    # 综合判断
    score = 100
    issues = []
    if term_density > 10:  # 每百字术语超 10 个 = 堆砌
        score -= 40
        issues.append(f"术语密度过高（每百字 {term_density:.1f} 个，>10 视为堆砌）")
    if not has_uncertainty:
        score -= 30
        issues.append("未声明任何不确定性，斩钉截铁地代学者发言")
    if not has_citations:
        score -= 15
        issues.append("无具体引用或案例")

    pass_threshold = 60
    return {
        "ok": score >= pass_threshold,
        "score": score,
        "term_density": round(term_density, 1),
        "has_uncertainty": has_uncertainty,
        "has_citations": has_citations,
        "issues": issues,
    }


def analyze(skill_path: Path, response_dir: Path, evidence_dir: Path | None = None) -> dict[str, Any]:
    static = static_check(skill_path, evidence_dir=evidence_dir)
    caricature_path = response_dir / "caricature_test.md"
    caricature = analyze_caricature(caricature_path)

    return {
        "static_check": static,
        "caricature_check": caricature,
        "overall_pass": static["pass"] and caricature["ok"],
    }


def print_analysis(result: dict[str, Any]) -> None:
    s = result["static_check"]
    c = result["caricature_check"]

    print("\n=== 静态检查 (v0.4: 8 项) ===")
    print(f"  得分：{s['score']} / 100")
    print(f"  通过：{'✓' if s['pass'] else '✗'}")
    if s["checks"].get("citation_anchor") is not None:
        ca = s["checks"]["citation_anchor"]
        print(f"  引文 page-anchor 核验：{ca['verified']}/{ca['total']} 可证 "
              f"({ca.get('pass_rate', 0):.0%}) — {'✓' if ca['pass'] else '✗'}")
    nb = s["checks"].get("narrative_bracketing")
    if nb is not None:
        print(f"  Narrative-bracketing：{nb['formative_events_total']} 个形成性事件，"
              f"{nb['without_bracketing']} 个缺双层标注 — {'✓' if nb['pass'] else '✗'}")
    if s["issues"]:
        print(f"  问题：")
        for i in s["issues"]:
            print(f"    - {i}")

    print(f"\n=== 漫画化检测 ===")
    print(f"  得分：{c['score']} / 100")
    print(f"  通过：{'✓' if c['ok'] else '✗'}")
    if c.get("issues"):
        print(f"  问题：")
        for i in c["issues"]:
            print(f"    - {i}")
    if "term_density" in c:
        print(f"  术语密度：每百字 {c['term_density']} 个")
        print(f"  含不确定性声明：{'是' if c.get('has_uncertainty') else '否'}")
        print(f"  含具体引用：{'是' if c.get('has_citations') else '否'}")

    print(f"\n=== 总判定 ===")
    print(f"  整体：{'✓ 通过' if result['overall_pass'] else '✗ 不通过，需迭代'}")


def main():
    p = argparse.ArgumentParser(description="Phase 4 质量验证（含漫画化检测）")
    p.add_argument("--prepare", action="store_true", help="生成测试任务")
    p.add_argument("--analyze", action="store_true", help="分析测试回答")
    p.add_argument("--skill", required=True, help="目标 skill 的 SKILL.md 路径")
    p.add_argument("--scholar", help="学者名（仅 --prepare 需要）")
    p.add_argument("--responses", default="_quality_test_responses",
                   help="测试回答目录")
    p.add_argument("--evidence-dir", default=None,
                   help="v0.4：_pdf_evidence 目录（启用引文 page-anchor 核验）")
    p.add_argument("--json-output", default=None, help="JSON 报告输出路径（可选）")
    args = p.parse_args()

    skill_path = Path(args.skill)
    if not skill_path.exists():
        print(f"ERROR: SKILL.md 不存在：{skill_path}", file=sys.stderr)
        sys.exit(1)

    evidence_dir = Path(args.evidence_dir).expanduser() if args.evidence_dir else None

    if args.prepare:
        if not args.scholar:
            p.error("--prepare 需要 --scholar")
        prepare_tests(skill_path, args.scholar, Path(args.responses))
    elif args.analyze:
        result = analyze(skill_path, Path(args.responses), evidence_dir=evidence_dir)
        print_analysis(result)
        if args.json_output:
            Path(args.json_output).write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        if not result["overall_pass"]:
            sys.exit(1)
    else:
        # 默认只跑静态检查（含 v0.4 新增检查项，若提供 --evidence-dir）
        result = static_check(skill_path, evidence_dir=evidence_dir)
        print(f"=== 静态检查 v0.4（仅 SKILL.md{'，含 page-anchor 核验' if evidence_dir else ''}） ===")
        print(f"得分：{result['score']} / 100")
        print(f"通过：{'✓' if result['pass'] else '✗'}")
        if result["checks"].get("citation_anchor") is not None:
            ca = result["checks"]["citation_anchor"]
            print(f"引文 page-anchor: {ca['verified']}/{ca['total']} 可证 ({ca.get('pass_rate', 0):.0%})")
        nb = result["checks"].get("narrative_bracketing")
        if nb is not None and nb["formative_events_total"] > 0:
            print(f"Narrative-bracketing: {nb['formative_events_total']} 个形成性事件，"
                  f"{nb['without_bracketing']} 个缺双层标注")
        if result["issues"]:
            print(f"\n问题：")
            for i in result["issues"]:
                print(f"  - {i}")
        if args.json_output:
            Path(args.json_output).write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        if not result["pass"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
