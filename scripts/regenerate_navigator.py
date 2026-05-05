#!/usr/bin/env python3
"""
regenerate_navigator.py · 从 _index.json 重生 _pdf_evidence/_navigator.md
========================================================================

scholar-wendao Workflow B 工具,在 extract_pdf_evidence.py 跑后或新 PDF
intake 后调用,刷新 _navigator.md(蒸馏导航文件)。

输入：_pdf_evidence/_index.json (extract_pdf_evidence 输出)
输出：_pdf_evidence/_navigator.md

用法：
  python3 scripts/regenerate_navigator.py \\
      --evidence-dir examples/stiegler-perspective/_pdf_evidence \\
      [--scholar-name "Bernard Stiegler"]

许可：MIT
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# 默认重要概念列表（按 _concepts.json 的 keys 顺序）
DEFAULT_CONCEPTS_ORDER = [
    "tertiary_retention", "epiphylogenesis", "pharmacology",
    "general_organology", "symbolic_misery", "proletarianization",
    "grammatization", "disruption", "neganthropy",
]


def regenerate(evidence_dir: Path, scholar_name: str = "") -> str:
    index_path = evidence_dir / "_index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"_index.json 不存在：{index_path}")
    items = json.loads(index_path.read_text(encoding="utf-8"))

    # 分类
    ok_items = [i for i in items if i.get("status") == "ok"]
    readable = [i for i in ok_items if (i.get("empty_pages") or 0) < 50
                and (i.get("total_chars") or 0) > 0]
    scanned = [i for i in ok_items if (i.get("empty_pages") or 0) >= 50
               or (i.get("total_chars") or 0) == 0]
    metadata_fragments = [i for i in readable if (i.get("pages") or 0) < 10
                          and (i.get("total_concept_hits") or 0) == 0]
    # 从 readable 移除 metadata_fragments
    readable_main = [i for i in readable if i not in metadata_fragments]

    # 概念命中矩阵
    concept_keys = DEFAULT_CONCEPTS_ORDER
    if readable_main:
        # 从第一个 readable item 推断真实 concept keys（如果与默认不一致）
        first_hits = readable_main[0].get("hits_per_concept", {})
        if first_hits:
            # 取 union
            all_concepts = set(concept_keys)
            for r in readable_main:
                all_concepts.update((r.get("hits_per_concept") or {}).keys())
            # 保持默认顺序优先,其他附加
            extra = sorted(all_concepts - set(concept_keys))
            concept_keys = concept_keys + extra

    # 计算每概念 top-3 anchor
    concept_top: dict[str, list[tuple[str, int]]] = {}
    for c in concept_keys:
        ranked: list[tuple[str, int]] = []
        for r in readable_main:
            n = (r.get("hits_per_concept") or {}).get(c, 0)
            if n > 0:
                ranked.append((r.get("book", ""), n))
        ranked.sort(key=lambda x: -x[1])
        concept_top[c] = ranked[:3]

    # 概念跨全库总命中
    concept_totals: dict[str, int] = {c: 0 for c in concept_keys}
    for r in readable_main:
        for c, n in (r.get("hits_per_concept") or {}).items():
            concept_totals[c] = concept_totals.get(c, 0) + n

    # 排序 readable_main 按 total_concept_hits 降序(为推荐阅读序)
    readable_main_sorted = sorted(readable_main,
                                  key=lambda r: -(r.get("total_concept_hits") or 0))

    # ========================================
    # 渲染 markdown
    # ========================================
    md: list[str] = []
    title_scholar = scholar_name or "本案例"
    md.append(f"# `_pdf_evidence/` Navigator · 自动生成")
    md.append("")
    md.append(f"> 由 `scripts/regenerate_navigator.py` 从 `_index.json` 自动生成（{datetime.now().strftime('%Y-%m-%d')}）。")
    md.append(f"> 本目录是 Workflow B 蒸馏的**强制证据库**——SKILL.md 每个核心概念的定义、引文、风格判断")
    md.append(f"> 都必须能追溯到这里某一份 `{{book}}.md` 的某一页。")
    md.append("")

    # 一、PDF 评估
    total_evidence = len(readable_main) + len(metadata_fragments) + len(scanned)
    total_chars = sum(r.get("total_chars", 0) for r in readable_main)
    total_hits = sum(r.get("total_concept_hits", 0) for r in readable_main)

    md.append(f"## 一、PDF 评估总览（共 {total_evidence} 部）")
    md.append("")
    md.append(f"- 可机读主要来源(≥10 页 + 有概念命中):**{len(readable_main)} 部** · 总 {total_chars:,} 字符 · 总 {total_hits} concept hits")
    md.append(f"- 元数据片段(目录/序言/版权页):{len(metadata_fragments)} 部")
    md.append(f"- 待 OCR(扫描无文字层):{len(scanned)} 部 · v0.5 OCR backlog")
    md.append("")

    md.append(f"### 可机读主要来源({len(readable_main)} 部)")
    md.append("")
    md.append(f"| 文件 | 页 | empty | chars | total hits |")
    md.append(f"| --- | ---: | ---: | ---: | ---: |")
    for r in readable_main_sorted:
        md.append(f"| {r['book']} | {r.get('pages','')} | {r.get('empty_pages','')} | {r.get('total_chars',0):,} | **{r.get('total_concept_hits',0)}** |")
    md.append("")

    if metadata_fragments:
        md.append(f"### 元数据片段({len(metadata_fragments)} 部 · 不参与蒸馏)")
        md.append("")
        for m in metadata_fragments:
            md.append(f"- `{m['book']}` ({m.get('pages','')} 页)")
        md.append("")

    if scanned:
        md.append(f"### 待 OCR({len(scanned)} 部 · v0.5 backlog)")
        md.append("")
        for s in scanned:
            md.append(f"- `{s['book']}` ({s.get('pages','')} 页 · empty={s.get('empty_pages','')})")
        md.append("")
        md.append("**OCR 命令**:")
        md.append("```")
        md.append("brew install ocrmypdf  # 一次性")
        md.append("ocrmypdf --language fra+eng+chi_sim --skip-text input.pdf input.pdf")
        md.append("# OCR 完后重跑:")
        md.append("python3 scripts/extract_pdf_evidence.py --filter \"<filename>.pdf\" --force ...")
        md.append("```")
        md.append("")

    # 二、9 概念 × top-3 anchor
    md.append(f"## 二、概念 × top-3 anchor 矩阵")
    md.append("")
    md.append("每条 = `[hits 数] book stem`。**Workflow B Phase 2.1** 强制概念条目的「证据来源」小节链接 top-3 anchor。")
    md.append("")
    md.append(f"| 概念 | rank 1 | rank 2 | rank 3 | 全库总 |")
    md.append(f"| --- | --- | --- | --- | ---: |")
    for c in concept_keys:
        top = concept_top[c]
        cells = []
        for i in range(3):
            if i < len(top):
                book, n = top[i]
                cells.append(f"{n} {book[:30]}")
            else:
                cells.append("—")
        md.append(f"| `{c}` | {cells[0]} | {cells[1]} | {cells[2]} | {concept_totals.get(c, 0)} |")
    md.append("")

    # 三、Phase 2 蒸馏推荐阅读序
    md.append(f"## 三、Workflow B 蒸馏推荐阅读序(按命中数降序)")
    md.append("")
    for i, r in enumerate(readable_main_sorted[:10], 1):
        size_kb = round(r.get("total_chars", 0) / 1000, 1)
        md.append(f"{i}. **`{r['book']}.md`** ({r.get('pages',0)} 页 / {size_kb}K 字 / {r.get('total_concept_hits',0)} hits)")
    md.append("")

    # 四、统计上限
    md.append(f"## 四、本次提取的统计上限")
    md.append("")
    md.append(f"- `--head 30 --tail 30 --context 200 --max-hits 50`(extract_pdf_evidence.py 默认)")
    md.append(f"- 大书中段(p.30+ 到 p.last-30)未取样;如需深度,单独 `--head 999 --tail 0` 重跑某部")
    md.append(f"- CJK 概念词用子串匹配(无 `\\b` 边界),可能少量误命中")
    md.append("")

    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser(description="Regenerate _navigator.md from _index.json")
    ap.add_argument("--evidence-dir", required=True,
                    help="_pdf_evidence/ 目录")
    ap.add_argument("--scholar-name", default="",
                    help="学者名(可选,用于标题)")
    ap.add_argument("--output", default="",
                    help="输出文件路径(默认 {evidence-dir}/_navigator.md)")
    args = ap.parse_args()

    evidence_dir = Path(args.evidence_dir).expanduser()
    md_text = regenerate(evidence_dir, args.scholar_name)

    out = Path(args.output).expanduser() if args.output else (evidence_dir / "_navigator.md")
    out.write_text(md_text, encoding="utf-8")
    print(f"✓ {out} 重生 ({len(md_text.splitlines())} 行)", file=sys.stderr)


if __name__ == "__main__":
    main()
