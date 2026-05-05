#!/usr/bin/env python3
"""
harvest_oa_publishers.py · Tier 2 OA 出版社 harvester (v0.4.3)
=================================================================

scholar-wendao Workflow A.1 中的 OA 资料发现工具。

为什么这个脚本存在
------------------
v0.4.2 实战暴露：annas-archive 全面被 Cloudflare/ParkLogic 反爬阻断，
但仍有大量 Stiegler 后期作品通过合法 OA 出版社发布（Open Humanities
Press, DOAB, OAPEN, Punctum, Open Book Publishers, archive.org 等）。

本脚本系统化挖掘这些 OA 源，对 Workflow A.1 提供 Tier 2 自动化补充：
  - DOAB API （Directory of Open Access Books, 广覆盖元数据）
  - Open Humanities Press（直接 title URL pattern, Critical Climate Change 系列等）
  - archive.org IA Scholar API（学者公开档案）
  - OAPEN handle 解析

输出与 _acquisition_manifest.json 兼容的 v0.4.2 schema：
  acquisition_tier: 2 (友好 scrape)
  acquisition_status: discovered_oa（待用户决定 intake）
  pdf_url: 直链
  acquisition_hints: [来源出版社, 系列名, 等]

用法：
  python3 scripts/harvest_oa_publishers.py "Bernard Stiegler" \\
    --output examples/{slug}-perspective/references/research/ \\
    --slug stiegler

  # 只跑特定源:
  python3 scripts/harvest_oa_publishers.py "Stiegler" --sources doab,ohp,ia

依赖：requests, pyyaml

设计:
  - 不重造轮子,优先用 API,回退到 HTML 解析
  - 失败优雅降级:某 source 不可达不影响其他
  - 输出统一 schema, 可直接 merge 到 _acquisition_manifest.json

许可：MIT
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

try:
    import requests
except ImportError:
    print("ERROR: pip install requests", file=sys.stderr); sys.exit(1)


HEADERS = {
    "User-Agent": "scholar-wendao/0.4.3 (https://github.com/tizzy916/scholar-wendao-skill)"
}
TIMEOUT = 25


# ============================================================
# Source 1: DOAB API
# ============================================================

def harvest_doab(scholar: str) -> list[dict[str, Any]]:
    """DOAB REST API: /rest/search?query=<q>&expand=metadata"""
    print(f"  [DOAB] 搜 {scholar!r} …", file=sys.stderr)
    url = f"https://directory.doabooks.org/rest/search"
    try:
        r = requests.get(url, params={"query": scholar, "expand": "metadata"},
                         headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"    ⚠️  DOAB 失败：{e}", file=sys.stderr)
        return []

    items: list[dict[str, Any]] = []
    for d in data:
        title = d.get("name", "")
        handle = d.get("handle", "")
        meta_dict = {m["key"]: m["value"] for m in d.get("metadata", []) if m.get("key")}

        # 提取年份
        year_str = meta_dict.get("dc.date.issued", "")
        year = int(year_str[:4]) if year_str[:4].isdigit() else None

        # DOAB handle 没有直接 PDF；转化为 OAPEN handle
        oapen_uri = meta_dict.get("oapen.relation.isPublishedBy", "")

        # author check
        authors = meta_dict.get("dc.contributor.author", "")
        if not authors and "creator" in meta_dict:
            authors = meta_dict.get("dc.creator", "")

        # 仅含学者名才纳入
        scholar_lower = scholar.lower()
        if scholar_lower not in (title + " " + authors).lower():
            continue

        items.append({
            "source": "doab",
            "title": title,
            "year": year,
            "author": authors[:100],
            "publisher": meta_dict.get("dc.publisher", ""),
            "language": meta_dict.get("dc.language", ""),
            "doab_handle": handle,
            "oapen_handle": oapen_uri,
            "doab_url": f"https://directory.doabooks.org/handle/{handle}" if handle else None,
            "pdf_url": None,  # DOAB no direct PDF in API
            "discovered_via": "doab_api",
        })

    print(f"    ✓ {len(items)} matches", file=sys.stderr)
    return items


# ============================================================
# Source 2: Open Humanities Press (OHP)
# ============================================================

# OHP 已知 Stiegler 直接相关标题（从 v0.4.2 实战发现）
OHP_KNOWN_STIEGLER_TITLES = {
    "the-neganthropocene": ("The Neganthropocene", 2018, "en", "Stiegler_2018_The-Neganthropocene.pdf"),
    "bifurcate": ("Bifurcate: There Is No Alternative", 2021, "en", "Stiegler_2021_Bifurcate.pdf"),
}

# OHP 间接相关（编辑作品 / 内含 Stiegler 章节 / 学生作品）
OHP_RELATED_TITLES = {
    "psychopolitical-anaphylaxis": ("Psychopolitical Anaphylaxis (Ross 2021, on Stiegler)",
                                     2021, "en", "Ross_2021_Psychopolitical-Anaphylaxis.pdf"),
    "telemorphosis": ("Telemorphosis: Theory in the Era of Climate Change",
                      2012, "en", "Cohen_2012_Telemorphosis.pdf"),
}


def harvest_ohp(scholar: str) -> list[dict[str, Any]]:
    """Open Humanities Press: 直接试已知 Stiegler / 相关标题的 URL pattern。"""
    print(f"  [OHP] 探测已知 Stiegler 系列标题 …", file=sys.stderr)
    items: list[dict[str, Any]] = []

    # 仅当 scholar 是 Stiegler 相关才用这个 mapping
    is_stiegler = "stiegler" in scholar.lower()

    candidates = {}
    if is_stiegler:
        candidates.update(OHP_KNOWN_STIEGLER_TITLES)
        candidates.update(OHP_RELATED_TITLES)
    # TODO v0.5: 通用化为通用 OHP catalog scrape(需要 OHP RSS / sitemap)

    for slug, (title, year, lang, pdf_filename) in candidates.items():
        title_url = f"https://openhumanitiespress.org/books/titles/{slug}/"
        pdf_url = f"http://openhumanitiespress.org/books/download/{pdf_filename}"

        # HEAD 请求验证 PDF 真存在
        try:
            r = requests.head(pdf_url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                items.append({
                    "source": "ohp",
                    "title": title,
                    "year": year,
                    "author": "Bernard Stiegler" if "stiegler" in pdf_filename.lower() else "",
                    "publisher": "Open Humanities Press",
                    "language": lang,
                    "title_url": title_url,
                    "pdf_url": pdf_url,
                    "pdf_size_bytes": int(r.headers.get("content-length", 0)) or None,
                    "discovered_via": "ohp_known_titles",
                    "is_direct_stiegler": "stiegler" in pdf_filename.lower(),
                })
                size_mb = int(r.headers.get("content-length", 0)) / 1024 / 1024
                print(f"    ✓ {slug} ({size_mb:.1f} MB)", file=sys.stderr)
        except Exception as e:
            print(f"    ⚠️  {slug}: {e}", file=sys.stderr)
            continue
        time.sleep(0.5)

    print(f"    ✓ OHP: {len(items)} OA PDFs", file=sys.stderr)
    return items


# ============================================================
# Source 3: archive.org Internet Archive Scholar / texts
# ============================================================

def harvest_archive_org(scholar: str) -> list[dict[str, Any]]:
    """archive.org advancedsearch API."""
    print(f"  [archive.org] 搜 {scholar!r} (texts) …", file=sys.stderr)
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": f'creator:"{scholar}" AND mediatype:texts',
        "fl[]": ["identifier", "title", "year", "creator", "mediatype",
                 "language", "publisher", "format"],
        "rows": 50,
        "output": "json",
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"    ⚠️  archive.org 失败：{e}", file=sys.stderr)
        return []

    docs = data.get("response", {}).get("docs", [])
    items: list[dict[str, Any]] = []
    for d in docs:
        ident = d.get("identifier")
        if not ident:
            continue
        # IA 详情页 + 推断 PDF 直链
        details_url = f"https://archive.org/details/{ident}"
        # PDF 直链通常是 https://archive.org/download/{ident}/{ident}.pdf
        # 但实际文件名可能不同;让 intake 时探测
        download_dir = f"https://archive.org/download/{ident}/"

        items.append({
            "source": "archive.org",
            "title": d.get("title", ""),
            "year": int(d["year"]) if d.get("year") and str(d["year"]).isdigit() else None,
            "author": d.get("creator", "") if isinstance(d.get("creator"), str)
                      else (d.get("creator", [""])[0] if d.get("creator") else ""),
            "language": d.get("language", "") if isinstance(d.get("language"), str)
                        else (d.get("language", [""])[0] if d.get("language") else ""),
            "publisher": d.get("publisher", "") if isinstance(d.get("publisher"), str)
                         else (d.get("publisher", [""])[0] if d.get("publisher") else ""),
            "ia_identifier": ident,
            "details_url": details_url,
            "download_dir_url": download_dir,
            "pdf_url": None,  # 待 intake 时探测真 PDF 文件名
            "discovered_via": "archive_org_texts",
        })

    print(f"    ✓ {len(items)} archive.org texts", file=sys.stderr)
    return items


# ============================================================
# Source 4: OAPEN library (handle 解析为 PDF)
# ============================================================

def harvest_oapen(scholar: str) -> list[dict[str, Any]]:
    """OAPEN 通过 DOAB handle 拉详细 metadata + bitstream URL。"""
    # 实测 OAPEN /rest/search 端点超时;留 placeholder
    print(f"  [OAPEN] 跳过(API 不稳定;待 v0.4.4 用 OPDS feed 替代)", file=sys.stderr)
    return []


# ============================================================
# 合并 + 去重 + 写出
# ============================================================

def merge_into_acquisition_manifest(harvest_items: list[dict[str, Any]],
                                    manifest_path: Path,
                                    scholar_slug: str,
                                    dry_run: bool = False) -> dict[str, int]:
    """把 harvest 结果 merge 到 _acquisition_manifest.json (v0.4.2 schema)。

    返回 {added, updated, skipped}。
    """
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = {"scholar_slug": scholar_slug, "items": [], "stats": {}}

    items = data.setdefault("items", [])

    def title_key(t: str, year: Any) -> str:
        # v0.4.3 规范：归一化空格 / 下划线 / 标点,case-insensitive
        norm = re.sub(r"[^\w]+", "", (t or "").lower())
        return f"{norm}{year}"

    existing_titles = {title_key(i.get("title", ""), i.get("year", "")): i for i in items}

    counts = {"added": 0, "updated": 0, "skipped": 0}

    for h in harvest_items:
        key = title_key(h.get("title", ""), h.get("year", ""))
        if key in existing_titles:
            # 更新现有条目（升级 acquisition_tier 从 4 → 2 + 加 pdf_url）
            existing = existing_titles[key]
            if h.get("pdf_url"):
                existing["acquisition_tier"] = 2
                # v0.4.3 修：不要把 intake_completed 降级为 discovered_oa
                if existing.get("acquisition_status") != "intake_completed":
                    existing["acquisition_status"] = "discovered_oa"
                existing["pdf_url"] = h["pdf_url"]
                existing.setdefault("acquisition_hints", []).insert(0,
                    f"OA 直链: {h['source']} ({h.get('publisher', 'unknown')})")
                counts["updated"] += 1
            else:
                counts["skipped"] += 1
        else:
            # 新增
            new_id = f"{scholar_slug}-{h.get('year', '0000')}-{re.sub(r'[^a-z0-9]+', '-', (h.get('title', '') or 'untitled').lower()[:30])}-{h.get('language', 'und')}"
            items.append({
                "id": new_id,
                "title": h.get("title", ""),
                "year": h.get("year"),
                "language": h.get("language"),
                "type": "book",
                "publisher": h.get("publisher", ""),
                "doi": None,
                "openalex_id": None,
                "acquisition_tier": 2 if h.get("pdf_url") else 3,
                "priority": "P1",  # 新发现的默认 P1, 用户可手动升 P0
                "acquisition_status": "discovered_oa" if h.get("pdf_url") else "manifest_only",
                "acquisition_hints": [
                    f"OA 直链: {h.get('source')} ({h.get('publisher', '')})",
                    f"discovered_via: {h.get('discovered_via', '')}",
                ],
                "pdf_url": h.get("pdf_url"),
                "details_url": h.get("details_url") or h.get("title_url") or h.get("doab_url"),
                "intended_filename": None,  # 由用户 / intake 决定
                "intake_completed_at": None,
                "manually_added": False,
                "discovered_by": "harvest_oa_publishers.py",
            })
            counts["added"] += 1

    if not dry_run:
        # 重新计算 stats
        data["stats"] = {
            "total_items": len(items),
            "tier_1": sum(1 for i in items if i.get("acquisition_tier") == 1),
            "tier_2": sum(1 for i in items if i.get("acquisition_tier") == 2),
            "tier_3": sum(1 for i in items if i.get("acquisition_tier") == 3),
            "tier_4": sum(1 for i in items if i.get("acquisition_tier") == 4),
            "p0": sum(1 for i in items if i.get("priority") == "P0"),
            "p1": sum(1 for i in items if i.get("priority") == "P1"),
            "p2": sum(1 for i in items if i.get("priority") == "P2"),
            "intake_completed": sum(1 for i in items if i.get("acquisition_status") == "intake_completed"),
            "discovered_oa": sum(1 for i in items if i.get("acquisition_status") == "discovered_oa"),
        }
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                 encoding="utf-8")

    return counts


# ============================================================
# 主流程
# ============================================================

SOURCES = {
    "doab": harvest_doab,
    "ohp": harvest_ohp,
    "ia": harvest_archive_org,
    "oapen": harvest_oapen,
}


def main():
    ap = argparse.ArgumentParser(description="OA 出版社 harvester (Tier 2)")
    ap.add_argument("scholar", help="学者全名,如 'Bernard Stiegler'")
    ap.add_argument("--output", default=".", help="输出目录(放 _oa_publishers_harvest.json)")
    ap.add_argument("--slug", help="学者 slug,用于新增 manifest 条目 ID")
    ap.add_argument("--manifest",
                    help="_acquisition_manifest.json 路径,提供则 merge")
    ap.add_argument("--sources", default="doab,ohp,ia",
                    help=f"要跑的源,逗号分隔 (可选: {','.join(SOURCES)})")
    ap.add_argument("--dry-run", action="store_true",
                    help="不写文件,只打印结果")
    args = ap.parse_args()

    sources_to_run = [s.strip() for s in args.sources.split(",") if s.strip()]
    invalid = set(sources_to_run) - set(SOURCES.keys())
    if invalid:
        print(f"ERROR: 未知 source: {invalid}", file=sys.stderr); sys.exit(1)

    out_dir = Path(args.output).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Harvest OA publishers for {args.scholar!r} ===\n", file=sys.stderr)
    all_items: list[dict[str, Any]] = []
    for s in sources_to_run:
        items = SOURCES[s](args.scholar)
        all_items.extend(items)
        time.sleep(1)

    print(f"\n=== 合计 {len(all_items)} 条 OA 候选 ===", file=sys.stderr)

    # 写 harvest 原始结果
    harvest_path = out_dir / "_oa_publishers_harvest.json"
    if not args.dry_run:
        harvest_path.write_text(
            json.dumps({"scholar": args.scholar, "items": all_items}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"  写入: {harvest_path}", file=sys.stderr)

    # 可选:merge 到现有 acquisition_manifest
    if args.manifest:
        manifest_path = Path(args.manifest).expanduser()
        slug = args.slug or args.scholar.lower().replace(" ", "-")
        counts = merge_into_acquisition_manifest(
            all_items, manifest_path, slug, dry_run=args.dry_run
        )
        print(f"\n=== Merge 到 {manifest_path.name} ===", file=sys.stderr)
        print(f"  + 新增: {counts['added']}", file=sys.stderr)
        print(f"  ~ 更新: {counts['updated']}", file=sys.stderr)
        print(f"  - 跳过: {counts['skipped']}", file=sys.stderr)


if __name__ == "__main__":
    main()
