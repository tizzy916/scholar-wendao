#!/usr/bin/env python3
"""
generate_library_cards.py · Phase 2.9 执行器（v0.4.1）
=====================================================

为每部本地 PDF 生成 / 更新 Obsidian Library Card。

输入：
  - _pdf_evidence/{book}.md   (extract_pdf_evidence.py 输出)
  - 07-archive.json            (harvest_works.py 输出，OpenAlex metadata)
  - _library_config.md         (含 v0.4.1 frontmatter，定义 vault 路径)
  - _concepts.json             (用于关键词推断)

行为：
  - 对每个 _pdf_evidence/{book}.md，匹配 archive.json 的对应 work
  - 已有 Card → 在 frontmatter 后追加 "📎 v0.4 PDF Evidence Anchors" 小节
    （保留用户手写的 引用章节 / 文献笔记 wikilink 等）
  - 不存在 Card → 用模板生成全新 Card（按用户 Vault 现有 Stiegler2013/2014 模板）

输出位置：
  根据 config 的 vault_archive_path + library_cards_path 写到用户 Vault
  例：~/.../02 · Knowledge 知识库/Library 数字图书馆/Cards/{ScholarPrefix}{year}.md

许可：MIT
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from datetime import datetime

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr); sys.exit(1)


# ============================================================
# 配置解析
# ============================================================

def parse_config(config_path: Path) -> dict[str, Any]:
    """读取 _library_config.md 的 frontmatter（YAML）。"""
    text = config_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n([\s\S]+?)\n---", text)
    if not m:
        raise ValueError(f"{config_path} 缺少 YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}


# ============================================================
# Evidence parser
# ============================================================

def parse_evidence(evidence_md: Path) -> dict[str, Any]:
    """从 _pdf_evidence/{book}.md 解析 metadata + concept hits + sample quotes。"""
    text = evidence_md.read_text(encoding="utf-8")

    # 头部 metadata（"# Title\n- source: ...\n- pages: ..."）
    title_m = re.search(r"^# (.+)$", text, re.MULTILINE)
    pages_m = re.search(r"\*\*pages\*\*:\s*(\d+)", text)
    empty_m = re.search(r"\*\*empty pages.*?\*\*:\s*(\d+)", text)
    chars_m = re.search(r"\*\*total chars extracted\*\*:\s*([\d,]+)", text)
    source_m = re.search(r"\*\*source\*\*:\s*`([^`]+)`", text)

    # 概念命中分布
    hits_per_concept: dict[str, int] = {}
    for cm in re.finditer(r"### `([^`]+)` — (\d+) hits", text):
        hits_per_concept[cm.group(1)] = int(cm.group(2))

    # Top 引用片段（取每个概念的前 1 个 hit，最多 8 条）
    top_quotes: list[dict[str, Any]] = []
    for cm in re.finditer(r"### `([^`]+)` — \d+ hits\s*\n\s*\n([\s\S]+?)(?=\n### `|\Z)", text):
        concept = cm.group(1)
        block = cm.group(2)
        # 第一条 hit
        first_hit = re.search(r"-\s*\*\*p\.(\d+)\*\*\s*\[`([^`]+)`\]:\s*(.+?)$",
                              block, re.MULTILINE)
        if first_hit:
            top_quotes.append({
                "concept": concept,
                "page": int(first_hit.group(1)),
                "term": first_hit.group(2),
                "context": first_hit.group(3).strip()[:300],
            })
        if len(top_quotes) >= 8:
            break

    # 一句话摘要：取 head pages 第一个非空段（前 200 字）
    head_match = re.search(r"## Head pages.*?\n\s*\n### p\.\d+\s*\n\s*\n([^\n]+)", text)
    summary = head_match.group(1).strip()[:200] if head_match else ""

    return {
        "evidence_filename": evidence_md.stem,
        "title_raw": title_m.group(1) if title_m else evidence_md.stem,
        "pages": int(pages_m.group(1)) if pages_m else 0,
        "empty_pages": int(empty_m.group(1)) if empty_m else 0,
        "total_chars": int(chars_m.group(1).replace(",", "")) if chars_m else 0,
        "source_path": source_m.group(1) if source_m else "",
        "hits_per_concept": hits_per_concept,
        "top_quotes": top_quotes,
        "summary": summary,
    }


# ============================================================
# Archive metadata matcher
# ============================================================

def match_archive_entry(book_stem: str, archive: dict[str, Any]) -> dict[str, Any] | None:
    """根据 _pdf_evidence/{book}.md 的 stem 匹配 archive.json 的 work。"""
    works = archive.get("works", [])

    # 提取 stem 中的 year
    year_m = re.search(r"(\d{4})", book_stem)
    target_year = int(year_m.group(1)) if year_m else None
    if not target_year:
        return None

    # 简化：取年份匹配的第一个 type=book 作品
    candidates = [w for w in works if w.get("year") == target_year and w.get("type") == "book"]
    if candidates:
        return candidates[0]

    # 退而求其次：年份匹配的任意 type
    candidates = [w for w in works if w.get("year") == target_year]
    if candidates:
        return candidates[0]

    return None


# ============================================================
# Card 渲染
# ============================================================

CARD_TEMPLATE = """---
title: "{title_quoted}"
author: "{author}"
year: {year}
grade: "A"
has_pdf: true
status: unread
tags:
  - library
{tags_yaml}
{versions_yaml}---

# 🔴 {author_abbrev}, {year}

**关键词:** {keywords}
**原文:** [[{library_files_path}/{pdf_filename}|📄 PDF]]

## 📚 完整引用（APA 7th）

{apa_citation}

---

## 一句话摘要
{summary}

## 引用章节
**论文**:(待论文写作时填写)
**章节**:(待论文写作时填写)

---

## 📝 论文引用摘录

> [!note] v0.4 PDF Evidence Anchors （由 scholar-wendao 自动生成）
> 完整 evidence 见 [[{slug}-perspective/_pdf_evidence/{evidence_basename}|{evidence_basename}]]
> 总页数 {pages} · empty pages {empty_pages} · 提取字数 {total_chars}
> 概念命中分布: {hit_summary}

{top_quotes_md}

---

## 🔗 关联
- 文献笔记:[[《{title_brief}》读书笔记]] (待写)
- 人物:[[{people_path}/{scholar_name}|{scholar_name}]]
- Perspective Skill:[[{slug}-perspective/SKILL|{scholar_name_en}-perspective skill]]
"""


def build_apa_citation(arch: dict[str, Any], evidence: dict[str, Any], scholar_name_en: str) -> str:
    """构造 APA 7th 引用。"""
    if not arch:
        # archive 找不到对应 work：用 evidence 自带的标题
        return f"{scholar_name_en}. ({evidence.get('title_raw', '')})."

    title = arch.get("title", "Untitled")
    year = arch.get("year", "")
    pub = arch.get("publisher", "")
    coauthors = arch.get("coauthors") or [scholar_name_en]
    author_part = coauthors[0] if coauthors else scholar_name_en

    parts = [f"{author_part}.", f"({year}).", f"*{title}*."]
    if pub:
        parts.append(f"{pub}.")
    return " ".join(parts)


def build_versions_yaml(arch: dict[str, Any] | None) -> str:
    """如果 archive 含 multilingual versions 信息，构造 versions: 字段。"""
    if not arch:
        return ""
    lang = arch.get("language", "")
    if not lang or lang == "und":
        return ""
    # 极简版：只标当前 PDF 的语言
    return f'versions:\n  {lang}: "(本卡片对应)"\n'


def render_top_quotes_md(top_quotes: list[dict[str, Any]]) -> str:
    """渲染 Top 引用片段为 markdown。"""
    if not top_quotes:
        return "_(无概念命中。可能为扫描 PDF 无文字层；建议 OCR 后重跑 extract_pdf_evidence.py。)_"
    out = []
    for q in top_quotes:
        out.append(f"### p. {q['page']}（概念: `{q['concept']}` · 匹配: `{q['term']}`）")
        out.append("")
        out.append(f"> {q['context']}")
        out.append("")
    return "\n".join(out)


def render_card(
    evidence: dict[str, Any],
    arch: dict[str, Any] | None,
    config: dict[str, Any],
    pdf_filename: str,
) -> str:
    """生成 Card 的 markdown 字符串。"""
    scholar_name = config.get("scholar_name", "Unknown")
    scholar_name_en = config.get("scholar_name_en", "Unknown")
    slug = config.get("scholar_slug", "unknown")
    library_files_path = config.get("library_files_path", "Library/_files")
    people_path = config.get("people_path", "People")

    year = arch.get("year") if arch else 0
    year_str = str(year) if year else "0000"
    title_raw = arch.get("title", evidence.get("title_raw", "")) if arch else evidence.get("title_raw", "")

    # 关键词：取 hits_per_concept 前 3
    hits_sorted = sorted(evidence["hits_per_concept"].items(), key=lambda kv: -kv[1])
    top_concepts = [c for c, n in hits_sorted[:3] if n > 0]
    keywords = "、".join(top_concepts) if top_concepts else "(待补)"

    # tags
    tag_lines: list[str] = []
    if "philosophy" not in tag_lines:
        tag_lines.append("  - philosophy")
    if any("technic" in c.lower() or "technology" in c.lower() for c in top_concepts):
        tag_lines.append("  - tech-studies")
    tags_yaml = "\n".join(tag_lines) + "\n" if tag_lines else ""

    # title for frontmatter (escaped)
    title_for_fm = f"{scholar_name_en} ({year_str}). {title_raw}".replace('"', "'")

    # author abbrev
    author_abbrev = scholar_name_en.split()[-1][:8]

    # title_brief 中文/缩写
    title_brief = title_raw.split(":")[0][:30]

    # hit summary
    hit_summary = ", ".join(f"{c}={n}" for c, n in hits_sorted if n > 0) or "(无命中)"

    return CARD_TEMPLATE.format(
        title_quoted=title_for_fm,
        author=scholar_name_en,
        year=year_str,
        tags_yaml=tags_yaml,
        versions_yaml=build_versions_yaml(arch),
        author_abbrev=author_abbrev,
        keywords=keywords,
        library_files_path=library_files_path,
        pdf_filename=pdf_filename,
        apa_citation=build_apa_citation(arch, evidence, scholar_name_en),
        summary=evidence.get("summary", "(待补)") or "(待补)",
        slug=slug,
        evidence_basename=evidence["evidence_filename"],
        pages=evidence["pages"],
        empty_pages=evidence["empty_pages"],
        total_chars=f"{evidence['total_chars']:,}",
        hit_summary=hit_summary,
        top_quotes_md=render_top_quotes_md(evidence["top_quotes"]),
        title_brief=title_brief,
        people_path=people_path,
        scholar_name=scholar_name,
        scholar_name_en=scholar_name_en,
    )


# ============================================================
# 增量更新（已存在 Card 时，仅在 frontmatter 后插入 evidence anchors 段）
# ============================================================

V04_ANCHOR_HEADER = "## 📎 v0.4 PDF Evidence Anchors"


def upsert_evidence_anchors(existing_card_path: Path, evidence: dict[str, Any], config: dict[str, Any]) -> str:
    """在已有 Card 中追加 / 替换 'v0.4 PDF Evidence Anchors' 段。"""
    text = existing_card_path.read_text(encoding="utf-8")

    slug = config.get("scholar_slug", "unknown")
    hit_summary = ", ".join(f"{c}={n}" for c, n in
                            sorted(evidence["hits_per_concept"].items(), key=lambda kv: -kv[1])
                            if n > 0) or "(无命中)"

    block = f"""\n\n{V04_ANCHOR_HEADER}

> 由 scholar-wendao v0.4.1 自动从本地 PDF 抽取（{datetime.now().strftime("%Y-%m-%d")}）。

- **evidence**: [[{slug}-perspective/_pdf_evidence/{evidence['evidence_filename']}|{evidence['evidence_filename']}]]
- **页数 / 提取字数 / empty 页**: {evidence['pages']} / {evidence['total_chars']:,} / {evidence['empty_pages']}
- **概念命中**: {hit_summary}

### Top 概念锚点片段

{render_top_quotes_md(evidence['top_quotes'])}
"""

    # 如果已存在该段，替换
    pattern = re.compile(rf"\n*{re.escape(V04_ANCHOR_HEADER)}[\s\S]*?(?=\n## |\Z)")
    if pattern.search(text):
        text = pattern.sub(block, text)
    else:
        text = text.rstrip() + block

    return text


# ============================================================
# 主流程
# ============================================================

def main():
    ap = argparse.ArgumentParser(description="Phase 2.9: Generate / update Library Cards")
    ap.add_argument("--config", required=True,
                    help="_library_config.md 路径（含 v0.4.1 frontmatter）")
    ap.add_argument("--evidence-dir", required=True,
                    help="_pdf_evidence/ 目录")
    ap.add_argument("--archive-json", required=True,
                    help="07-archive.json 路径")
    ap.add_argument("--dry-run", action="store_true",
                    help="不写文件，只 stdout 显示打算做什么")
    args = ap.parse_args()

    cfg = parse_config(Path(args.config).expanduser())
    archive = json.loads(Path(args.archive_json).expanduser().read_text(encoding="utf-8"))

    vault_root = Path(cfg["vault_archive_path"]).expanduser()
    cards_dir = vault_root / cfg["library_cards_path"]
    files_dir = vault_root / cfg["library_files_path"]
    prefix = cfg.get("file_prefix", "")

    if not args.dry_run:
        cards_dir.mkdir(parents=True, exist_ok=True)

    evidence_dir = Path(args.evidence_dir).expanduser()
    evidence_files = [f for f in evidence_dir.glob("*.md") if not f.name.startswith("_")]
    print(f"待生成 / 更新 {len(evidence_files)} 部 Card …", file=sys.stderr)

    new_count = 0
    upserted_count = 0
    skipped_count = 0

    for ev_md in sorted(evidence_files):
        evidence = parse_evidence(ev_md)
        arch = match_archive_entry(ev_md.stem, archive)

        # 构造 PDF 文件名（library_files 内的扁平命名）
        pdf_filename = ev_md.stem + ".pdf"
        pdf_path = files_dir / pdf_filename
        if not pdf_path.exists():
            # 没有对应 PDF，跳过（可能是 evidence 文件名不一致）
            print(f"  ! 跳过 {ev_md.stem}：PDF 不存在 {pdf_path}", file=sys.stderr)
            skipped_count += 1
            continue

        # v0.4.1 简化映射规则：每个 evidence 一对一 Card，名字直接用 evidence stem。
        # 仅当 evidence stem 形如 "{prefix}{year}"（无 _suffix）才使用主 Card 名。
        # 这样 Stiegler2017 → Stiegler2017.md，但 Stiegler2017_Contents → Stiegler2017_Contents.md。
        target_card = cards_dir / f"{ev_md.stem}.md"

        if target_card.exists():
            new_text = upsert_evidence_anchors(target_card, evidence, cfg)
            print(f"  + UPSERT {target_card.name}", file=sys.stderr)
            upserted_count += 1
        else:
            new_text = render_card(evidence, arch, cfg, pdf_filename)
            print(f"  * NEW    {target_card.name}", file=sys.stderr)
            new_count += 1

        if not args.dry_run:
            target_card.write_text(new_text, encoding="utf-8")

    print(f"\n=== 完成 ===", file=sys.stderr)
    print(f"  新建 Card:   {new_count}", file=sys.stderr)
    print(f"  增量更新:    {upserted_count}", file=sys.stderr)
    print(f"  跳过:       {skipped_count}", file=sys.stderr)
    print(f"  Cards 目录:  {cards_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
