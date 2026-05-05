#!/usr/bin/env python3
"""
extract_pdf_evidence.py · v0.4 P0 #1
=====================================

对本地 PDF 库逐部抽取「证据片段」给 Phase 2 二次蒸馏使用。

为什么这个脚本存在
------------------
v0.3 暴露的根本问题：Phase 1 写「先读本地素材」但 Phase 2 实际上没读 PDF
全文，只读了用户已整理的 Obsidian Card 元数据。这导致蒸馏深度不足。

v0.4 强制 Phase 1 多一步：调用本脚本对每部本地 PDF 抽出关键章节文本 +
针对目标概念做 keyword 搜索 + 输出带页码的上下文片段，作为 Phase 2 必须
读入的「证据库」。

输出结构
--------
对每部 PDF 产出一份 markdown：
  examples/{slug}-perspective/_pdf_evidence/{book_basename}.md

每份 markdown 包含三部分：
  1. Head pages —— 前 N 页（默认 30）：通常含序、目录、首章开头
  2. Tail pages —— 末 N 页（默认 30）：通常含末章、索引、参考文献
  3. Concept anchor search —— 对每个目标概念多语言变体在全书 grep，
     输出 ±200 字上下文 + 页码，每概念最多 50 hits

依赖
----
- pymupdf (PyMuPDF)：pip install pymupdf

法律提示
--------
本脚本只对 *用户本地已合法持有* 的 PDF 做文本抽取，不联网、不分发。
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import pymupdf  # PyMuPDF
except ImportError:
    print("ERROR: 缺少依赖 'pymupdf'。请安装：pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def extract_book(
    pdf_path: Path,
    concept_terms: dict[str, list[str]],
    head_pages: int = 30,
    tail_pages: int = 30,
    context_chars: int = 200,
    max_hits_per_concept: int = 50,
) -> dict[str, Any]:
    """抽取一部 PDF 的关键证据。

    concept_terms: {concept_id: [term1, term2, ...]} —— 多语言术语映射，
    所有术语会以 case-insensitive whole-word 在全书 grep。
    """
    doc = pymupdf.open(pdf_path)
    n_pages = len(doc)

    sections: dict[str, Any] = {
        "metadata": {
            "title": (doc.metadata or {}).get("title") or pdf_path.stem,
            "author": (doc.metadata or {}).get("author"),
            "pages": n_pages,
            "source": str(pdf_path),
        },
        "head": [],
        "tail": [],
        "concept_hits": {cid: [] for cid in concept_terms},
        "stats": {"empty_pages": 0, "total_chars": 0},
    }

    # 预编译 concept 正则
    # 注意：CJK 字不能用 \b 边界 —— Python 的 \b 在 CJK 字符间无效。
    # 对纯 ASCII 术语用 \b，对含 CJK 的术语用「不被另一个 CJK 包围」启发式。
    def is_cjk_term(s: str) -> bool:
        return any("一" <= c <= "鿿" for c in s)

    compiled: dict[str, list[tuple[str, re.Pattern]]] = {}
    for cid, terms in concept_terms.items():
        compiled[cid] = []
        for t in terms:
            if is_cjk_term(t):
                # CJK：直接子串匹配（会有少量误命中，权衡精度/召回）
                pat = re.compile(re.escape(t), re.IGNORECASE)
            else:
                pat = re.compile(rf"\b{re.escape(t)}\b", re.IGNORECASE)
            compiled[cid].append((t, pat))

    # head
    for i in range(min(head_pages, n_pages)):
        text = doc[i].get_text("text").strip()
        sections["stats"]["total_chars"] += len(text)
        if not text:
            sections["stats"]["empty_pages"] += 1
            continue
        sections["head"].append({"page": i + 1, "text": text})

    # tail
    tail_start = max(head_pages, n_pages - tail_pages)  # 防止 head/tail 重叠
    for i in range(tail_start, n_pages):
        text = doc[i].get_text("text").strip()
        sections["stats"]["total_chars"] += len(text)
        if not text:
            sections["stats"]["empty_pages"] += 1
            continue
        sections["tail"].append({"page": i + 1, "text": text})

    # concept search across full doc（包括 head/tail，方便统一 hits 视图）
    hit_count: dict[str, int] = {cid: 0 for cid in concept_terms}
    for i in range(n_pages):
        text = doc[i].get_text("text")
        if not text:
            continue
        for cid, term_pats in compiled.items():
            if hit_count[cid] >= max_hits_per_concept:
                continue
            # 每页对每概念至多取 1 hit（避免单页 spam）
            page_hit = False
            for term, pat in term_pats:
                if page_hit:
                    break
                m = pat.search(text)
                if m:
                    start = max(0, m.start() - context_chars)
                    end = min(len(text), m.end() + context_chars)
                    ctx = text[start:end].replace("\n", " ").strip()
                    sections["concept_hits"][cid].append({
                        "page": i + 1,
                        "term_matched": term,
                        "context": ctx,
                    })
                    hit_count[cid] += 1
                    page_hit = True

    doc.close()
    return sections


def render_markdown(sections: dict[str, Any]) -> str:
    md: list[str] = []
    m = sections["metadata"]
    s = sections["stats"]

    md.append(f"# {m['title']}")
    md.append("")
    md.append(f"- **source**: `{m['source']}`")
    md.append(f"- **pages**: {m['pages']}")
    if m.get("author"):
        md.append(f"- **author (PDF metadata)**: {m['author']}")
    md.append(f"- **empty pages (likely scanned/no text layer)**: {s['empty_pages']}")
    md.append(f"- **total chars extracted**: {s['total_chars']:,}")
    md.append("")
    md.append("---")
    md.append("")

    # Head
    md.append(f"## Head pages (frontmatter / TOC / first chapter, {len(sections['head'])} pages)")
    md.append("")
    for p in sections["head"]:
        md.append(f"### p.{p['page']}")
        md.append("")
        md.append(p["text"])
        md.append("")

    # Tail
    md.append(f"## Tail pages (last chapter / index / bibliography, {len(sections['tail'])} pages)")
    md.append("")
    for p in sections["tail"]:
        md.append(f"### p.{p['page']}")
        md.append("")
        md.append(p["text"])
        md.append("")

    # Concept hits
    md.append("## Concept anchor search")
    md.append("")
    md.append("> Each hit = first occurrence on a page; ±200 chars context.")
    md.append("")
    for cid, hits in sections["concept_hits"].items():
        md.append(f"### `{cid}` — {len(hits)} hits")
        md.append("")
        if not hits:
            md.append("_(no occurrences in this volume)_")
            md.append("")
            continue
        for h in hits:
            md.append(f"- **p.{h['page']}** [`{h['term_matched']}`]: …{h['context']}…")
        md.append("")

    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser(
        description="Extract key sections + concept-anchored evidence from local PDFs"
    )
    ap.add_argument("--library", required=True,
                    help="Directory containing PDFs (e.g. ~/.../Library 数字图书馆/_files)")
    ap.add_argument("--filter", default="*.pdf",
                    help="Glob pattern within library (default '*.pdf'; e.g. 'Stiegler*.pdf')")
    ap.add_argument("--concepts", required=True,
                    help="JSON file: {concept_id: [term1, term2, ...]} (multilingual terms)")
    ap.add_argument("--out", required=True,
                    help="Output directory for evidence markdowns")
    ap.add_argument("--head", type=int, default=30,
                    help="Number of head pages to extract verbatim (default 30)")
    ap.add_argument("--tail", type=int, default=30,
                    help="Number of tail pages to extract verbatim (default 30)")
    ap.add_argument("--context", type=int, default=200,
                    help="Chars of context around each concept hit (default 200)")
    ap.add_argument("--max-hits", type=int, default=50,
                    help="Max hits per concept per book (default 50)")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing evidence markdowns")
    args = ap.parse_args()

    concept_terms = json.loads(Path(args.concepts).read_text(encoding="utf-8"))
    if not isinstance(concept_terms, dict):
        print("ERROR: --concepts JSON must be a dict {concept_id: [terms...]}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    lib = Path(args.library).expanduser()
    pdfs = sorted(lib.glob(args.filter))
    print(f"Found {len(pdfs)} PDFs in {lib} matching {args.filter!r}", file=sys.stderr)
    if not pdfs:
        sys.exit(0)

    summary: list[dict[str, Any]] = []
    for pdf in pdfs:
        slug = pdf.stem
        out = out_dir / f"{slug}.md"
        if out.exists() and out.stat().st_size > 0 and not args.force:
            print(f"  skip (exists): {slug}", file=sys.stderr)
            summary.append({"book": slug, "status": "skipped_exists"})
            continue
        print(f"  extracting: {slug}", file=sys.stderr)
        try:
            sections = extract_book(
                pdf, concept_terms,
                head_pages=args.head,
                tail_pages=args.tail,
                context_chars=args.context,
                max_hits_per_concept=args.max_hits,
            )
            md = render_markdown(sections)
            out.write_text(md, encoding="utf-8")
            total_hits = sum(len(v) for v in sections["concept_hits"].values())
            summary.append({
                "book": slug,
                "pages": sections["metadata"]["pages"],
                "empty_pages": sections["stats"]["empty_pages"],
                "total_chars": sections["stats"]["total_chars"],
                "total_concept_hits": total_hits,
                "hits_per_concept": {
                    c: len(h) for c, h in sections["concept_hits"].items()
                },
                "status": "ok",
            })
        except Exception as e:
            print(f"    FAILED: {e}", file=sys.stderr)
            summary.append({"book": slug, "status": "failed", "error": str(e)})

    (out_dir / "_index.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 终端摘要
    ok = sum(1 for s in summary if s.get("status") == "ok")
    skipped = sum(1 for s in summary if s.get("status") == "skipped_exists")
    failed = sum(1 for s in summary if s.get("status") == "failed")
    print(f"\n=== Done: ok={ok} skipped={skipped} failed={failed} ===", file=sys.stderr)
    print(f"Output: {out_dir}", file=sys.stderr)
    print(f"Index:  {out_dir / '_index.json'}", file=sys.stderr)


if __name__ == "__main__":
    main()
