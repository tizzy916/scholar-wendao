#!/usr/bin/env python3
"""
quality_check.py · Phase 4 质量验证（含漫画化检测）

为 scholar-wendao 的 Phase 4 服务：检查生成的 [scholar]-perspective skill
是否符合 5 项学术合规要求 + 通过漫画化检测。

测试项：
  4.1 已知测试（Sanity Check）—— 由 agent 执行
  4.2 边缘测试（Edge Case）—— 由 agent 执行
  4.3 漫画化检测（Caricature Test）⭐ 学者问道独有
  4.4 默会知识声明检查 —— 静态检查 SKILL.md
  4.5 通过标准评分 —— 静态检查

设计：
  4.1/4.2/4.3 需要让独立 agent 用新生成的 skill 跑测试，所以本脚本
  生成"测试任务"prompt，agent 执行后把回答存到指定文件，本脚本
  读取并分析（启发式 + 模式匹配）。

  4.4/4.5 是纯静态检查，不需要 LLM。

用法：
  # Step 1: 生成测试任务
  python3 quality_check.py --prepare \\
    --skill ~/.claude/skills/stiegler-perspective/SKILL.md

  # Step 2: agent 执行测试，把回答存到 _quality_test_responses/

  # Step 3: 分析结果
  python3 quality_check.py --analyze \\
    --skill ~/.claude/skills/stiegler-perspective/SKILL.md \\
    --responses _quality_test_responses/

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
# 静态检查：5 项必备声明 + 通过标准
# ===========================================================

REQUIRED_DECLARATIONS = {
    "polanyi": [r"波兰尼", r"默会", r"tacit\s+knowledge", r"Polanyi"],
    "fossilization": [r"化石化", r"调研时间", r"采集.*?截至", r"snapshot"],
    "public_vs_private": [r"公开.*?(私下|表演|展演)", r"前台", r"展演自我", r"performance"],
    "biographical_rhetoric": [r"传记修辞", r"叙事建构", r"narrative\s+construction"],
    "caricature": [r"漫画化", r"caricature", r"口头禅"],
}

# Phase 4 通过标准（来自 SKILL.md §4.5）
THRESHOLDS = {
    "concept_count_min": 3,
    "concept_count_max": 7,
    "heuristic_count_min": 5,
    "primary_source_ratio_min": 0.5,
    "biography_grade_required": True,
    "five_declarations_required": True,
}


def static_check(skill_path: Path) -> dict[str, Any]:
    text = skill_path.read_text(encoding="utf-8")
    results: dict[str, Any] = {
        "skill_path": str(skill_path),
        "checked_at": datetime.now().isoformat(),
        "checks": {},
        "score": 0,
        "issues": [],
    }

    # 1. 五大批评声明
    declarations = {}
    for key, patterns in REQUIRED_DECLARATIONS.items():
        present = any(re.search(pat, text, re.IGNORECASE) for pat in patterns)
        declarations[key] = present
        if not present:
            results["issues"].append(f"缺失诚实边界声明：{key}（任一关键词都未出现）")
    results["checks"]["five_declarations"] = declarations
    results["checks"]["five_declarations_pass"] = all(declarations.values())

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

    # 4. 调研时间
    has_research_date = bool(re.search(r"调研时间[：:]\s*\d{4}", text))
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

    # 计算总分（5 项 × 20 分）
    score = 0
    if results["checks"]["five_declarations_pass"]:
        score += 20
    if results["checks"]["concept_count_pass"]:
        score += 20
    if results["checks"]["heuristic_count_pass"]:
        score += 20
    if has_research_date:
        score += 10
    if default_lens_mode and has_optin_dialogue:
        score += 15
    pr = results["checks"].get("primary_ratio")
    if pr is not None and pr >= THRESHOLDS["primary_source_ratio_min"]:
        score += 15
    results["score"] = score
    results["pass"] = score >= 80 and not any(
        issue.startswith("缺失诚实边界") for issue in results["issues"]
    )

    return results


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


def analyze(skill_path: Path, response_dir: Path) -> dict[str, Any]:
    static = static_check(skill_path)
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

    print("\n=== 静态检查 ===")
    print(f"  得分：{s['score']} / 100")
    print(f"  通过：{'✓' if s['pass'] else '✗'}")
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
    p.add_argument("--json-output", default=None, help="JSON 报告输出路径（可选）")
    args = p.parse_args()

    skill_path = Path(args.skill)
    if not skill_path.exists():
        print(f"ERROR: SKILL.md 不存在：{skill_path}", file=sys.stderr)
        sys.exit(1)

    if args.prepare:
        if not args.scholar:
            p.error("--prepare 需要 --scholar")
        prepare_tests(skill_path, args.scholar, Path(args.responses))
    elif args.analyze:
        result = analyze(skill_path, Path(args.responses))
        print_analysis(result)
        if args.json_output:
            Path(args.json_output).write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        if not result["overall_pass"]:
            sys.exit(1)
    else:
        # 默认只跑静态检查
        result = static_check(skill_path)
        print(f"=== 静态检查（仅 SKILL.md，未执行测试） ===")
        print(f"得分：{result['score']} / 100")
        print(f"通过：{'✓' if result['pass'] else '✗'}")
        if result["issues"]:
            print(f"\n问题：")
            for i in result["issues"]:
                print(f"  - {i}")
        if not result["pass"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
