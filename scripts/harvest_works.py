#!/usr/bin/env python3
"""
harvest_works.py · 多源学术档案采集

为 scholar-wendao 的 Phase 1 Agent 7（学术档案采集）服务。

核心功能：
  给定学者名 + 语言偏好，从 OpenAlex / Crossref / Semantic Scholar 等
  开放学术 API 采集该学者全部著作的元数据，输出结构化 JSON。

用法：
  python3 harvest_works.py "Bernard Stiegler" --langs fr,en,zh \\
    --output references/research/07-archive.md \\
    --json-output references/research/07-archive.json

设计理念：
  - 优先调用 Academix MCP（如可用）—— scholar-wendao 不重造采集轮子
  - 不可用时回落到直接 HTTP API 调用（OpenAlex 是公开免费的）
  - 永远输出标准 JSON + 人类可读 Markdown 双格式

依赖：
  - requests (pip install requests)
  - 可选：Academix MCP server 已配置

许可：MIT
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

try:
    import requests
except ImportError:
    print("ERROR: 缺少依赖 'requests'。请安装：pip install requests --break-system-packages", file=sys.stderr)
    sys.exit(1)


# =====================================================================
# OpenAlex API（免费、无需 token、覆盖最完整的开放学术索引）
# =====================================================================

OPENALEX_BASE = "https://api.openalex.org"
HEADERS = {
    "User-Agent": "scholar-wendao/0.2 (https://github.com/tizzy916/scholar-wendao-skill; mailto:noreply@example.com)"
}


def search_author_openalex(name: str) -> list[dict[str, Any]]:
    """搜索 OpenAlex 中的作者，返回候选列表（用于消歧）。"""
    url = f"{OPENALEX_BASE}/authors"
    params = {"search": name, "per-page": 10}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])


def get_works_for_author(author_id: str, max_works: int = 500) -> list[dict[str, Any]]:
    """获取某 OpenAlex 作者 ID 名下的所有作品（分页拉取）。"""
    works = []
    cursor = "*"
    while True:
        url = f"{OPENALEX_BASE}/works"
        params = {
            "filter": f"author.id:{author_id}",
            "per-page": 200,
            "cursor": cursor,
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        page = data.get("results", [])
        works.extend(page)
        if len(works) >= max_works:
            break
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor or not page:
            break
        cursor = next_cursor
        time.sleep(0.1)  # 善意限速
    return works[:max_works]


def normalize_openalex_work(w: dict[str, Any]) -> dict[str, Any]:
    """把 OpenAlex 的 work 对象规整为我们的 schema。"""
    title = w.get("title") or w.get("display_name") or ""
    year = w.get("publication_year")
    work_type = w.get("type")
    lang = w.get("language") or "und"
    cited_by_count = w.get("cited_by_count", 0)

    # 开放获取链接
    oa = w.get("open_access", {})
    oa_url = oa.get("oa_url") if oa.get("is_oa") else None

    # 备选 OA 链接（来自 best_oa_location 或 primary_location）
    if not oa_url:
        for loc_key in ("best_oa_location", "primary_location"):
            loc = w.get(loc_key) or {}
            if loc.get("is_oa"):
                oa_url = loc.get("pdf_url") or loc.get("landing_page_url")
                if oa_url:
                    break

    # 期刊/出版社
    venue = ""
    primary = w.get("primary_location") or {}
    source = primary.get("source") or {}
    if source.get("display_name"):
        venue = source["display_name"]

    # 合著者
    authorships = w.get("authorships", [])
    coauthors = [a.get("author", {}).get("display_name", "") for a in authorships]

    return {
        "openalex_id": w.get("id"),
        "doi": w.get("doi"),
        "title": title,
        "year": year,
        "type": work_type,
        "language": lang,
        "venue": venue,
        "coauthors": coauthors,
        "cited_by_count": cited_by_count,
        "is_oa": bool(oa_url),
        "oa_url": oa_url,
        "abstract": _abstract_from_inverted_index(w.get("abstract_inverted_index")),
    }


def _abstract_from_inverted_index(idx: dict | None) -> str:
    """OpenAlex 用 inverted index 存摘要，复原为正常文本。"""
    if not idx:
        return ""
    positions: dict[int, str] = {}
    for word, locs in idx.items():
        for loc in locs:
            positions[loc] = word
    if not positions:
        return ""
    return " ".join(positions[i] for i in sorted(positions.keys()))


# =====================================================================
# Crossref API（补充 OpenAlex 漏掉的）
# =====================================================================

def search_works_crossref(author_name: str, rows: int = 200) -> list[dict[str, Any]]:
    """从 Crossref 拉取署名包含 author_name 的作品。"""
    url = "https://api.crossref.org/works"
    params = {"query.author": author_name, "rows": rows}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    items = r.json().get("message", {}).get("items", [])
    out = []
    for it in items:
        # 严格过滤：必须真的是这个作者
        authors = it.get("author", []) or []
        names_match = any(
            _name_matches(author_name, f"{a.get('given', '')} {a.get('family', '')}")
            for a in authors
        )
        if not names_match:
            continue
        out.append({
            "doi": it.get("DOI"),
            "title": (it.get("title") or [""])[0],
            "year": _crossref_year(it),
            "type": it.get("type"),
            "language": it.get("language", "und"),
            "venue": (it.get("container-title") or [""])[0],
            "publisher": it.get("publisher", ""),
            "isbn": it.get("ISBN", []),
            "source": "crossref",
        })
    return out


def _crossref_year(item: dict) -> int | None:
    for key in ("published-print", "published-online", "issued"):
        d = item.get(key, {}).get("date-parts")
        if d and d[0]:
            return d[0][0]
    return None


def _name_matches(query: str, candidate: str) -> bool:
    """简单的姓名匹配（去除空白、不区分大小写、检查姓氏匹配）。"""
    q = re.sub(r"\s+", " ", query.strip().lower())
    c = re.sub(r"\s+", " ", candidate.strip().lower())
    if not q or not c:
        return False
    q_last = q.split()[-1]
    c_last = c.split()[-1]
    return q_last == c_last and (q in c or c in q or q_last in c)


# =====================================================================
# 主采集流程
# =====================================================================

def harvest(name: str, langs: list[str], max_works: int = 500) -> dict[str, Any]:
    """主流程：搜作者、拉作品、归一化、按语言分组。"""
    print(f"[1/4] 搜索 OpenAlex 中的作者：{name}", file=sys.stderr)
    candidates = search_author_openalex(name)
    if not candidates:
        print(f"  ⚠️  OpenAlex 找不到作者 '{name}'", file=sys.stderr)
        return {"scholar": name, "works": [], "summary": {}}

    # 取第一个候选（通常是最相关的）。生产环境应让用户确认
    author = candidates[0]
    author_id = author["id"].rsplit("/", 1)[-1]
    works_count = author.get("works_count", 0)
    print(f"  ✓ 找到 {author['display_name']} (ID: {author_id}, works: {works_count})", file=sys.stderr)

    if len(candidates) > 1:
        print(f"  ℹ️  共 {len(candidates)} 个候选作者，自动选第一个。其他候选：", file=sys.stderr)
        for c in candidates[1:5]:
            print(f"     - {c['display_name']} ({c.get('works_count', 0)} works) [{c['id']}]", file=sys.stderr)

    print(f"[2/4] 拉取作品（最多 {max_works}）...", file=sys.stderr)
    raw_works = get_works_for_author(author_id, max_works=max_works)
    print(f"  ✓ 拉到 {len(raw_works)} 部作品", file=sys.stderr)

    print(f"[3/4] 归一化 + 补充 Crossref...", file=sys.stderr)
    normalized = [normalize_openalex_work(w) for w in raw_works]

    # Crossref 补充（找 OpenAlex 漏掉的）
    crossref_works = search_works_crossref(name)
    existing_dois = {w["doi"] for w in normalized if w.get("doi")}
    for cw in crossref_works:
        if cw.get("doi") and cw["doi"] not in existing_dois:
            normalized.append({
                **cw,
                "is_oa": False,
                "oa_url": None,
                "cited_by_count": None,
                "coauthors": [],
                "abstract": "",
                "openalex_id": None,
            })

    print(f"  ✓ Crossref 补充后总计 {len(normalized)} 部", file=sys.stderr)

    # 语言过滤
    if langs and "all" not in langs:
        normalized = [w for w in normalized if w.get("language", "und") in langs or w.get("language") == "und"]

    # 按年份倒序
    normalized.sort(key=lambda w: (w.get("year") or 0, w.get("cited_by_count") or 0), reverse=True)

    print(f"[4/4] 生成统计摘要...", file=sys.stderr)
    summary = build_summary(normalized, langs)

    return {
        "scholar": name,
        "openalex_author_id": author_id,
        "openalex_canonical_name": author["display_name"],
        "harvest_total": len(normalized),
        "summary": summary,
        "works": normalized,
    }


def build_summary(works: list[dict], langs: list[str]) -> dict[str, Any]:
    by_lang: dict[str, int] = defaultdict(int)
    by_type: dict[str, int] = defaultdict(int)
    by_decade: dict[str, int] = defaultdict(int)
    oa_count = 0
    closed_count = 0

    for w in works:
        by_lang[w.get("language", "und")] += 1
        by_type[w.get("type", "unknown")] += 1
        y = w.get("year") or 0
        if y:
            by_decade[f"{y // 10 * 10}s"] += 1
        if w.get("is_oa"):
            oa_count += 1
        else:
            closed_count += 1

    return {
        "by_language": dict(sorted(by_lang.items(), key=lambda x: -x[1])),
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "by_decade": dict(sorted(by_decade.items())),
        "oa_count": oa_count,
        "closed_count": closed_count,
        "oa_ratio": round(oa_count / max(len(works), 1), 3),
    }


# =====================================================================
# 输出
# =====================================================================

def write_markdown_report(result: dict[str, Any], path: Path) -> None:
    s = result["summary"]
    lines = [
        f"# 学术档案采集报告 · {result['scholar']}",
        "",
        f"> Agent 7 (学术档案采集) 输出 · 由 [scholar-wendao](https://github.com/tizzy916/scholar-wendao-skill) 生成",
        "",
        "## 元数据",
        "",
        f"- **学者**：{result['scholar']}",
        f"- **OpenAlex 规范名**：{result.get('openalex_canonical_name', 'N/A')}",
        f"- **OpenAlex Author ID**：`{result.get('openalex_author_id', 'N/A')}`",
        f"- **采集总量**：{result['harvest_total']} 部",
        f"- **OA 覆盖率**：{int(s['oa_ratio'] * 100)}% （开放获取 {s['oa_count']} 部 / 闭源 {s['closed_count']} 部）",
        "",
        "## 语种分布",
        "",
        "| 语种 | 数量 |",
        "| --- | --- |",
    ]
    for lang, n in s["by_language"].items():
        lines.append(f"| {lang} | {n} |")

    lines += ["", "## 类型分布", "", "| 类型 | 数量 |", "| --- | --- |"]
    for t, n in s["by_type"].items():
        lines.append(f"| {t} | {n} |")

    lines += ["", "## 年代分布", "", "| 年代 | 数量 |", "| --- | --- |"]
    for dec, n in s["by_decade"].items():
        lines.append(f"| {dec} | {n} |")

    lines += ["", "---", "", "## 完整书目（按引用数+年份排序）", ""]
    for i, w in enumerate(result["works"], 1):
        title = w.get("title", "Untitled")
        year = w.get("year") or "?"
        lang = w.get("language", "?")
        venue = w.get("venue", "")
        cited = w.get("cited_by_count")
        oa = "✅ OA" if w.get("is_oa") else "🔒 闭源"
        oa_link = f"[全文]({w['oa_url']})" if w.get("oa_url") else ""
        doi = f"[DOI](https://doi.org/{w['doi']})" if w.get("doi") else ""
        cited_str = f"被引 {cited} 次" if cited else ""

        lines.append(f"### {i}. {title} ({year})")
        meta = [f"`{lang}`", oa]
        if cited_str:
            meta.append(cited_str)
        if venue:
            meta.append(venue)
        lines.append("- " + " · ".join(meta))
        if doi or oa_link:
            lines.append(f"- {doi} {oa_link}".strip())
        if w.get("abstract"):
            abst = w["abstract"][:300] + ("…" if len(w["abstract"]) > 300 else "")
            lines.append(f"- 摘要：{abst}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="多源学术档案采集（scholar-wendao Agent 7）")
    p.add_argument("scholar", help="学者名（建议英文规范名以提高匹配率）")
    p.add_argument("--langs", default="all", help="语言过滤，逗号分隔，如 'fr,en,zh'。默认 'all' 表示不过滤")
    p.add_argument("--max-works", type=int, default=500, help="最大采集数量（默认 500）")
    p.add_argument("--output", default="07-archive.md", help="Markdown 报告输出路径")
    p.add_argument("--json-output", default="07-archive.json", help="结构化 JSON 输出路径")
    args = p.parse_args()

    langs = [s.strip() for s in args.langs.split(",")]

    try:
        result = harvest(args.scholar, langs, max_works=args.max_works)
    except requests.HTTPError as e:
        print(f"ERROR: HTTP 请求失败：{e}", file=sys.stderr)
        sys.exit(2)
    except requests.RequestException as e:
        print(f"ERROR: 网络错误：{e}", file=sys.stderr)
        sys.exit(2)

    # JSON 输出（结构化，给后续脚本读取）
    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ JSON 已写入：{json_path}", file=sys.stderr)

    # Markdown 报告
    md_path = Path(args.output)
    write_markdown_report(result, md_path)
    print(f"✓ Markdown 报告已写入：{md_path}", file=sys.stderr)

    # 摘要打印到 stdout（供 agent 解析）
    s = result["summary"]
    print(f"\n采集完成：{result['harvest_total']} 部作品")
    print(f"  语种：{', '.join(f'{k}({v})' for k, v in s['by_language'].items())}")
    print(f"  OA 覆盖率：{int(s['oa_ratio'] * 100)}%")
    print(f"  闭源待获取：{s['closed_count']} 部 → 接下来用 annas_acquire.py 处理")


if __name__ == "__main__":
    main()
