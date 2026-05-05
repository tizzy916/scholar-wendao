#!/usr/bin/env python3
"""
intake_manual_pdf.py · Phase A.4 主动导入入口（v0.4.2）
======================================================

scholar-wendao 双工作流架构中 Workflow A.4 的工具。
让用户手动下载的 PDF（来自 annas / 出版社 / 机构图书馆 / 任何源）
能以最低摩擦归档到 Library，并自动生成 Card + evidence。

使用场景：
  - annas 反爬严格无法自动下载，但用户从浏览器手动下了某本书
  - 用户从机构图书馆借阅扫描了某部专著
  - 用户找到了某本书的法语原版 PDF

设计原则：
  - **重复执行友好**：每次跑可以加 1 部到 N 部
  - **不破坏已有 Library 命名约定**：完全遵循 _library_config.md 的 archive_layout + file_prefix
  - **acquisition_manifest 自动更新**：手动导入的 PDF 被标记为 intake_completed
  - **dry-run 优先**：默认显示动作计划，加 --execute 才真正动文件

用法：
  # 基础（fully spec）
  python3 scripts/intake_manual_pdf.py \\
      ~/Downloads/Bifurquer-Bernard-Stiegler.pdf \\
      --config examples/stiegler-perspective/references/research/_library_config.md \\
      --year 2020 \\
      --slug Bifurquer \\
      --lang fr \\
      --execute

  # 关联 acquisition_manifest 中已有的条目
  python3 scripts/intake_manual_pdf.py PDF \\
      --config CONFIG \\
      --manifest-id stiegler-2020-bifurquer-fr \\
      --execute

  # 批量（多个 PDF + 自动从文件名推断 year/lang）
  python3 scripts/intake_manual_pdf.py \\
      ~/Downloads/*.pdf \\
      --config CONFIG \\
      --auto-infer \\
      --execute

许可：MIT
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr); sys.exit(1)


# ============================================================
# 配置解析
# ============================================================

def parse_config(config_path: Path) -> dict[str, Any]:
    text = config_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n([\s\S]+?)\n---", text)
    if not m:
        raise ValueError(f"{config_path} 缺少 YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}


# ============================================================
# 文件名推断（auto-infer 模式）
# ============================================================

def infer_year_from_filename(name: str) -> int | None:
    m = re.search(r"(?:^|[^0-9])(19\d{2}|20\d{2})(?:[^0-9]|$)", name)
    return int(m.group(1)) if m else None


def infer_lang_from_filename(name: str) -> str | None:
    """根据文件名关键词推断语言（v0.4.2 用 regex 边界避免 "Entr" 误匹配 "_en"）。"""
    lower = name.lower()
    # 严格：下划线后跟 lang 代码 + 边界（_ 或 . 或 末尾）
    m = re.search(r"_(fr|en|zh|de|es|it)(?:_|\.|$)", lower)
    if m:
        return m.group(1)
    # 关键词回退
    if any(t in lower for t in ["francais", "français", "galilée", "galilee", "_french"]):
        return "fr"
    if any(t in name for t in ["中文", "中译", "中译版"]) or "_chinese" in lower:
        return "zh"
    if "_english" in lower:
        return "en"
    if any(t in lower for t in ["_german", "deutsch"]):
        return "de"
    return None


def slugify_for_filename(s: str, max_len: int = 50) -> str:
    """把任意字符串转为安全文件名片段。"""
    s = re.sub(r"[^\w一-鿿\-]+", "_", s).strip("_")
    return s[:max_len]


# ============================================================
# 扁平命名构造
# ============================================================

def build_target_filename(prefix: str, year: int | None, slug: str | None,
                          lang: str | None, archive_layout: str) -> str:
    """构造目标 PDF 文件名 (按 _library_config 的 archive_layout)。"""
    parts: list[str] = []
    if archive_layout == "flat":
        # {prefix}{year}_{slug}[_{lang}].pdf
        head = f"{prefix or ''}{year or '0000'}"
        parts.append(head)
        if slug:
            parts.append(slugify_for_filename(slug))
        if lang and lang not in ("und", ""):
            parts.append(lang)
        return "_".join(parts) + ".pdf"
    else:
        # by-language: {year}_{slug}.pdf 在 {lang}/ 子目录
        head = f"{year or '0000'}"
        parts.append(head)
        if slug:
            parts.append(slugify_for_filename(slug))
        return "_".join(parts) + ".pdf"


def build_target_path(library_root: Path, filename: str, lang: str | None,
                      archive_layout: str) -> Path:
    if archive_layout == "by-language":
        return library_root / (lang or "und") / filename
    return library_root / filename


# ============================================================
# acquisition_manifest 更新
# ============================================================

def update_manifest(manifest_path: Path, manifest_id: str | None,
                    target_filename: str, source_path: Path,
                    year: int | None, slug: str | None, lang: str | None,
                    dry_run: bool) -> None:
    if not manifest_path.exists():
        # 初始化空 manifest
        if dry_run:
            print(f"  [dry-run] 会初始化 manifest: {manifest_path}", file=sys.stderr)
            return
        manifest_path.write_text(json.dumps({
            "scholar": "",
            "scholar_slug": "",
            "generated_at": datetime.now().date().isoformat(),
            "items": []
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = data.setdefault("items", [])

    # 查找已有条目
    existing = None
    if manifest_id:
        existing = next((i for i in items if i.get("id") == manifest_id), None)

    now = datetime.now().date().isoformat()
    if existing:
        existing["acquisition_status"] = "intake_completed"
        existing["intake_completed_at"] = now
        existing["actual_filename"] = target_filename
        existing["actual_source"] = str(source_path)
        if dry_run:
            print(f"  [dry-run] manifest: 标记 '{manifest_id}' = intake_completed", file=sys.stderr)
            return
    else:
        # 新增条目
        new_id = manifest_id or f"intake-{slugify_for_filename(target_filename, 30)}"
        items.append({
            "id": new_id,
            "title": slug or target_filename,
            "year": year,
            "language": lang,
            "type": "book",
            "acquisition_tier": 4,
            "priority": "P0",
            "acquisition_status": "intake_completed",
            "acquisition_hints": [],
            "intended_filename": target_filename,
            "actual_filename": target_filename,
            "actual_source": str(source_path),
            "intake_completed_at": now,
            "manually_added": True,
        })
        if dry_run:
            print(f"  [dry-run] manifest: 新增条目 '{new_id}'", file=sys.stderr)
            return

    manifest_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ============================================================
# 调用 extract_pdf_evidence + generate_library_cards
# ============================================================

def run_evidence_and_card(cfg: dict[str, Any], example_path: Path,
                          target_filename: str, dry_run: bool) -> None:
    repo_root = Path(cfg["project_repo_path"]).expanduser()
    scripts_dir = repo_root / "scripts"

    library_root = (Path(cfg["vault_archive_path"]).expanduser()
                    / cfg["library_files_path"])

    # extract_pdf_evidence (单文件)
    cmd_evidence = [
        "python3", str(scripts_dir / "extract_pdf_evidence.py"),
        "--library", str(library_root),
        "--filter", target_filename,
        "--concepts", str(example_path / "_pdf_evidence" / "_concepts.json"),
        "--out", str(example_path / "_pdf_evidence"),
        "--head", "30", "--tail", "30",
    ]
    print(f"\n  → extract_pdf_evidence:\n    {' '.join(cmd_evidence)}", file=sys.stderr)
    if not dry_run:
        result = subprocess.run(cmd_evidence, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ⚠️  extract_pdf_evidence 失败: {result.stderr}", file=sys.stderr)
        else:
            print(f"    ✓ extract done", file=sys.stderr)

    # generate_library_cards (full sweep；幂等)
    config_path = next(example_path.glob("references/research/_library_config.md"), None)
    if not config_path:
        return
    cmd_card = [
        "python3", str(scripts_dir / "generate_library_cards.py"),
        "--config", str(config_path),
        "--evidence-dir", str(example_path / "_pdf_evidence"),
        "--archive-json", str(example_path / "references/research/07-archive.json"),
    ]
    print(f"\n  → generate_library_cards:\n    {' '.join(cmd_card)}", file=sys.stderr)
    if not dry_run:
        result = subprocess.run(cmd_card, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ⚠️  generate_library_cards 失败: {result.stderr}", file=sys.stderr)
        else:
            # 显示 stdout 最后几行
            lines = result.stderr.strip().splitlines()[-5:]
            for line in lines:
                print(f"    {line}", file=sys.stderr)


# ============================================================
# 主流程
# ============================================================

def intake_one(pdf: Path, cfg: dict[str, Any], example_path: Path,
               year: int | None, slug: str | None, lang: str | None,
               manifest_id: str | None, copy_mode: bool, dry_run: bool) -> dict[str, Any]:

    library_root = (Path(cfg["vault_archive_path"]).expanduser()
                    / cfg["library_files_path"])
    archive_layout = cfg.get("archive_layout", "flat")
    file_prefix = cfg.get("file_prefix", "")

    target_filename = build_target_filename(file_prefix, year, slug, lang, archive_layout)
    target_path = build_target_path(library_root, target_filename, lang, archive_layout)

    print(f"\n=== {pdf.name} ===", file=sys.stderr)
    print(f"  source:    {pdf}", file=sys.stderr)
    print(f"  target:    {target_path}", file=sys.stderr)
    print(f"  layout:    {archive_layout}", file=sys.stderr)
    print(f"  mode:      {'copy' if copy_mode else 'move'}", file=sys.stderr)

    if target_path.exists():
        print(f"  ⚠️  目标已存在 — 跳过文件移动，仅刷新 evidence + Card", file=sys.stderr)
    else:
        if dry_run:
            print(f"  [dry-run] 会 {('copy' if copy_mode else 'move')} → {target_path}", file=sys.stderr)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if copy_mode:
                shutil.copy2(pdf, target_path)
            else:
                shutil.move(str(pdf), str(target_path))
            print(f"  ✓ {('copied' if copy_mode else 'moved')} OK", file=sys.stderr)

    # 更新 manifest
    manifest_path = example_path / "references/research/_acquisition_manifest.json"
    update_manifest(manifest_path, manifest_id, target_filename, pdf,
                    year, slug, lang, dry_run)

    # 跑 evidence + card
    run_evidence_and_card(cfg, example_path, target_filename, dry_run)

    return {
        "source": str(pdf),
        "target": str(target_path),
        "filename": target_filename,
        "manifest_id": manifest_id,
    }


def main():
    ap = argparse.ArgumentParser(description="Phase A.4 manual PDF intake")
    ap.add_argument("pdfs", nargs="+", help="一个或多个 PDF 文件路径")
    ap.add_argument("--config", required=True, help="_library_config.md 路径")
    ap.add_argument("--year", type=int, help="出版年份（不给则尝试 auto-infer）")
    ap.add_argument("--slug", help="书名 slug，用于扁平命名")
    ap.add_argument("--lang", help="语种 (fr/en/zh/...)；不给则尝试 auto-infer")
    ap.add_argument("--manifest-id", help="关联 _acquisition_manifest.json 中的条目 ID")
    ap.add_argument("--copy", action="store_true", help="复制源 PDF（默认 move）")
    ap.add_argument("--auto-infer", action="store_true",
                    help="批量模式下从文件名推断 year + lang")
    ap.add_argument("--execute", action="store_true",
                    help="执行实际动作（默认 dry-run）")
    args = ap.parse_args()

    cfg = parse_config(Path(args.config).expanduser())
    example_path = (Path(cfg["project_repo_path"]).expanduser()
                    / cfg["example_path"])

    if not args.execute:
        print("\n>>> DRY-RUN 模式（加 --execute 执行实际动作）<<<\n", file=sys.stderr)

    results = []
    for pdf_str in args.pdfs:
        pdf = Path(pdf_str).expanduser().resolve()
        if not pdf.exists() or not pdf.is_file() or pdf.suffix.lower() != ".pdf":
            print(f"  ⚠️  跳过非 PDF 或不存在: {pdf}", file=sys.stderr)
            continue

        year = args.year
        lang = args.lang
        slug = args.slug

        if args.auto_infer:
            if year is None:
                year = infer_year_from_filename(pdf.stem)
            if lang is None:
                lang = infer_lang_from_filename(pdf.stem)
            if slug is None:
                # v0.4.2 修复：先去掉 file_prefix（避免 slug 重复出现 prefix）
                base = pdf.stem
                prefix = cfg.get("file_prefix", "")
                if prefix and base.lower().startswith(prefix.lower()):
                    base = base[len(prefix):]
                # 去掉年份
                base = re.sub(r"(?:^|[\s_-])(19|20)\d{2}(?:[\s_-]|$)", " ", base)
                # 去掉语种标记
                base = re.sub(r"_?(fr|en|zh|de|es|it)_?\b", "", base, flags=re.IGNORECASE)
                slug = slugify_for_filename(base.strip("-_ "), 40)

        results.append(intake_one(
            pdf, cfg, example_path,
            year=year, slug=slug, lang=lang,
            manifest_id=args.manifest_id,
            copy_mode=args.copy, dry_run=not args.execute,
        ))

    print(f"\n=== 完成 ===  ({len(results)} 部 PDF)", file=sys.stderr)
    for r in results:
        print(f"  {r['source']}\n    → {r['filename']}", file=sys.stderr)


if __name__ == "__main__":
    main()
