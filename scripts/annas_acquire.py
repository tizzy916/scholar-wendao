#!/usr/bin/env python3
"""
annas_acquire.py · Anna's Archive 学术著作获取（多语言版本优先级）

为 scholar-wendao 的 Phase 1 服务：处理 download_open_access.sh 之后
仍未获取的闭源专著。

核心功能：
  - 读取 harvest_works.py 输出的 JSON
  - 对每部 is_oa=false 的专著（type=book），按"原版语言 > 英译 > 其他"
    优先级在 Anna's Archive 搜索 + 下载
  - 至少保证一个语言版本被获取（设计理念之一）

依赖与认证：
  - 优先尝试 annas-py 库（pip install annas-py）
  - 或 annas-mcp（https://github.com/iosifache/annas-mcp）
  - 下载需要 Anna's Archive 会员 API key（捐助获得）
  - 设置环境变量：ANNAS_API_KEY=你的key

设计理念：
  - 不重造轮子，包装现有工具
  - 多语言优先级可配置（CLI 参数）
  - 失败优雅降级：API key 没设就只搜索不下载，输出待下载清单

许可：MIT

法律提示：
  Anna's Archive 是档案聚合服务，对版权状态因国家和作品而异。
  使用本脚本下载受版权保护的著作，由用户自行评估法律风险。
  本工具仅为学术研究提供便利，不参与版权判断。
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("ERROR: 缺少依赖 'requests'。请安装：pip install requests --break-system-packages", file=sys.stderr)
    sys.exit(1)

# 尝试导入 annas-py（可选）
try:
    import annas_py
    HAS_ANNAS_PY = True
except ImportError:
    HAS_ANNAS_PY = False


ANNAS_BASE = "https://annas-archive.org"
HEADERS = {
    "User-Agent": "scholar-wendao/0.2 (https://github.com/tizzy916/scholar-wendao-skill)"
}

# 默认语言优先级（可被 CLI 覆盖）
DEFAULT_LANG_PRIORITY = ["fr", "de", "en", "es", "it", "zh", "ja", "ru"]


def search_annas(title: str, author: str, lang: str | None = None) -> list[dict[str, Any]]:
    """搜索 Anna's Archive。优先用 annas-py 库，否则用直接 HTTP 调用。"""
    if HAS_ANNAS_PY:
        try:
            results = annas_py.search(f"{title} {author}", language=lang)
            return [_normalize_annaspy(r) for r in results[:10]]
        except Exception as e:
            print(f"  ⚠️  annas-py 搜索失败：{e}，回落到 HTTP", file=sys.stderr)

    # 直接 HTTP（解析搜索页面）—— 简化版，主要用于元数据匹配
    query = f'"{title}" "{author}"'
    url = f"{ANNAS_BASE}/search"
    params: dict[str, str] = {"q": query}
    if lang:
        params["lang"] = lang
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return _parse_annas_html(r.text)
    except requests.RequestException as e:
        print(f"  ⚠️  HTTP 搜索失败：{e}", file=sys.stderr)
        return []


def _normalize_annaspy(r: Any) -> dict[str, Any]:
    """把 annas-py 返回的对象规整为统一格式。"""
    return {
        "title": getattr(r, "title", ""),
        "author": getattr(r, "authors", [""])[0] if getattr(r, "authors", None) else "",
        "year": getattr(r, "year", None),
        "language": getattr(r, "language", "und"),
        "filetype": getattr(r, "format", ""),
        "filesize_mb": getattr(r, "filesize_mb", None),
        "md5": getattr(r, "md5", None),
        "download_url": getattr(r, "download_url", None),
    }


def _parse_annas_html(html: str) -> list[dict[str, Any]]:
    """从 Anna's Archive 搜索 HTML 中提取条目。

    简化解析（生产中建议用 annas-py 或 annas-mcp）。
    返回少量信息——主要是 md5（用于后续构造下载链接）。
    """
    results = []
    # 解析每个搜索结果的 md5
    for m in re.finditer(r'/md5/([a-f0-9]{32})"[^>]*>(.*?)</a>', html, re.DOTALL)[:10]:
        md5 = m.group(1)
        snippet = m.group(2)
        title_match = re.search(r"<h3[^>]*>(.*?)</h3>", snippet, re.DOTALL)
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else ""
        results.append({
            "title": title,
            "md5": md5,
            "language": "und",
            "filetype": "unknown",
            "filesize_mb": None,
            "download_url": None,
        })
    return results


def pick_best_match(
    candidates: list[dict[str, Any]],
    target_title: str,
    target_author: str,
    lang_priority: list[str],
) -> dict[str, Any] | None:
    """从候选中按"语种优先级 + 标题相似度 + filetype"挑最佳。"""
    if not candidates:
        return None

    target_norm = _norm_title(target_title)

    def score(c: dict[str, Any]) -> tuple[int, int, float]:
        # 语种排名（越前越好，所以取负值）
        lang = (c.get("language") or "und").lower()
        try:
            lang_score = -lang_priority.index(lang)
        except ValueError:
            lang_score = -100  # 不在优先级列表里，最低
        # 文件类型（PDF/EPUB > 其他）
        ft = (c.get("filetype") or "").lower()
        if "pdf" in ft:
            ft_score = 2
        elif "epub" in ft:
            ft_score = 1
        else:
            ft_score = 0
        # 标题相似度（简易）
        title_sim = _title_similarity(target_norm, _norm_title(c.get("title", "")))
        return (lang_score, ft_score, title_sim)

    return max(candidates, key=score)


def _norm_title(s: str) -> str:
    return re.sub(r"\W+", "", (s or "").lower())


def _title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    if short in long_:
        return 1.0
    # 简单字符级重合
    common = sum(1 for c in short if c in long_)
    return common / max(len(short), 1)


def download_via_md5(md5: str, dest: Path, api_key: str | None) -> bool:
    """通过 Anna's Archive 的 md5 直接获取下载链接并下载。

    需要会员 API key 才能拿到稳定下载源。无 API key 时跳过，
    返回 False。
    """
    if not api_key:
        return False

    # Anna's Archive 会员 API：通过 md5 拿下载 URL
    api_url = f"{ANNAS_BASE}/dyn/api/fast_download.json"
    try:
        r = requests.get(
            api_url,
            params={"md5": md5, "key": api_key},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        download_url = data.get("download_url")
        if not download_url:
            print(f"    ⚠️  API 未返回 download_url：{data.get('error', 'unknown')}", file=sys.stderr)
            return False
    except requests.RequestException as e:
        print(f"    ⚠️  API 调用失败：{e}", file=sys.stderr)
        return False

    # 下载文件
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(download_url, headers=HEADERS, stream=True, timeout=120) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"    ⚠️  下载失败：{e}", file=sys.stderr)
        if dest.exists():
            dest.unlink()
        return False


def acquire_for_scholar(
    json_input: Path,
    output_dir: Path,
    lang_priority: list[str],
    api_key: str | None,
    only_books: bool,
    archive_layout: str = "flat",
    prefix: str = "",
    manifest_only: bool = False,
) -> None:
    """v0.4：archive_layout 'flat'/'by-language'；manifest_only 跳过下载只生清单。"""
    data = json.loads(json_input.read_text(encoding="utf-8"))
    works = data["works"]

    # 过滤：只处理闭源专著（默认）或所有闭源作品
    targets = [w for w in works if not w.get("is_oa")]
    if only_books:
        targets = [w for w in targets if w.get("type") == "book"]

    print(f"待 Anna's Archive 获取：{len(targets)} 部 "
          f"(layout={archive_layout}, prefix='{prefix}')", file=sys.stderr)
    if manifest_only:
        print("ℹ️  --manifest-only：仅搜索 + 写清单，不实际下载（v0.4 新增）", file=sys.stderr)
    elif not api_key:
        print("⚠️  未设置 ANNAS_API_KEY 环境变量。将只生成搜索/下载清单，不实际下载。", file=sys.stderr)
        print("   获取 API key: https://annas-archive.org/donate", file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "_acquisition_manifest.json"
    failed_path = output_dir / "_acquisition_failed.json"

    manifest = []
    failed = []
    success = 0

    for i, w in enumerate(targets, 1):
        title = w.get("title", "Untitled")
        coauthors = w.get("coauthors") or []
        author = coauthors[0] if coauthors else data.get("scholar", "")

        print(f"\n[{i}/{len(targets)}] {title[:60]}", file=sys.stderr)

        # 按语言优先级搜索
        best = None
        all_candidates = []
        for lang in lang_priority:
            candidates = search_annas(title, author, lang=lang)
            all_candidates.extend(candidates)
            time.sleep(0.5)  # 善意限速
        if not all_candidates:
            # 不限语言再搜一次
            all_candidates = search_annas(title, author, lang=None)

        best = pick_best_match(all_candidates, title, author, lang_priority)
        if not best:
            print(f"  ✗ 无匹配", file=sys.stderr)
            failed.append({"title": title, "reason": "no_match"})
            continue

        lang = best.get("language", "und")
        year = w.get("year", "0000")
        manifest_entry = {
            "title": title,
            "author": author,
            "year": year,
            "doi": w.get("doi"),
            "matched_md5": best.get("md5"),
            "matched_lang": lang,
            "matched_title": best.get("title"),
        }

        # v0.4：archive_layout 决定输出路径
        safe_title = re.sub(r"\W+", "_", title)[:60].strip("_")
        if archive_layout == "flat":
            if lang and lang != "und":
                fname = f"{prefix}{year}_{safe_title}_{lang}.pdf"
            else:
                fname = f"{prefix}{year}_{safe_title}.pdf"
            dest = output_dir / fname
        else:  # by-language
            dest = output_dir / lang / f"{year}_{safe_title}.pdf"

        # manifest-only 模式或缺 api_key/md5 → 只记不下载
        if manifest_only or not api_key or not best.get("md5"):
            print(f"  ⏸  仅记录: md5={best.get('md5')}, lang={lang}, "
                  f"target={dest.name}", file=sys.stderr)
            manifest_entry["status"] = "manifest_only"
            manifest_entry["target_path"] = str(dest)
            manifest.append(manifest_entry)
            time.sleep(0.5)
            continue

        # 真实下载
        if dest.exists():
            print(f"  ✓ 已存在，跳过：{dest.name}", file=sys.stderr)
            manifest_entry["status"] = "already_exists"
            manifest_entry["path"] = str(dest)
            success += 1
        elif download_via_md5(best["md5"], dest, api_key):
            print(f"  ✓ 下载成功：{dest.name}", file=sys.stderr)
            manifest_entry["status"] = "downloaded"
            manifest_entry["path"] = str(dest)
            success += 1
        else:
            print(f"  ✗ 下载失败", file=sys.stderr)
            manifest_entry["status"] = "download_failed"
            failed.append({"title": title, "md5": best["md5"], "reason": "download_failed"})

        manifest.append(manifest_entry)
        time.sleep(1)  # 善意限速

    # 写 manifest
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        failed_path.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")

    # 摘要
    print(f"\n=== 完成 ===", file=sys.stderr)
    print(f"匹配到：{len(manifest)} / {len(targets)}", file=sys.stderr)
    print(f"实际下载：{success}", file=sys.stderr)
    print(f"失败：{len(failed)}", file=sys.stderr)
    print(f"manifest：{manifest_path}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description="Anna's Archive 学术著作获取（v0.4，多语言优先级）")
    p.add_argument("json_input", help="harvest_works.py 输出的 JSON")
    p.add_argument("-o", "--output", default="sources/works", help="输出目录")
    p.add_argument("--lang-priority", default=",".join(DEFAULT_LANG_PRIORITY),
                   help=f"语言优先级，逗号分隔。默认 '{','.join(DEFAULT_LANG_PRIORITY)}'")
    p.add_argument("--all-types", action="store_true",
                   help="处理所有闭源作品（默认仅 book 类型）")
    # v0.4 P3 #9：archive_layout
    p.add_argument("--archive-layout", choices=["flat", "by-language"], default="flat",
                   help="输出布局：flat (扁平命名，v0.4 推荐) 或 by-language (子目录)")
    p.add_argument("--prefix", default="",
                   help="flat 布局下的文件名前缀（如 'Stiegler'）")
    # v0.4 P2 #8：manifest-only
    p.add_argument("--manifest-only", action="store_true",
                   help="仅搜索 + 写清单，不实际下载（受限网络 / 提前规划用）")
    args = p.parse_args()

    api_key = os.environ.get("ANNAS_API_KEY")
    lang_priority = [s.strip() for s in args.lang_priority.split(",") if s.strip()]

    acquire_for_scholar(
        Path(args.json_input),
        Path(args.output).expanduser(),
        lang_priority,
        api_key,
        only_books=not args.all_types,
        archive_layout=args.archive_layout,
        prefix=args.prefix,
        manifest_only=args.manifest_only,
    )


if __name__ == "__main__":
    main()
