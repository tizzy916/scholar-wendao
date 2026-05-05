#!/usr/bin/env python3
"""
sync_to_vault.py · Phase 5.5 执行器（v0.4.1）
=============================================

把 examples/{slug}-perspective/ 内的 references/research/ + references/biography/
+ _pdf_evidence/ 同步到用户 Vault 的对应位置。

输入：_library_config.md（v0.4.1 frontmatter 含 vault_archive_path 与 7 个子路径）

执行：
  1. 复制 references/research/   → {vault}/{project_workspace_path}/research/
  2. 复制 references/biography/  → {vault}/{project_workspace_path}/biography/
  3. 复制 _pdf_evidence/         → {vault}/{project_workspace_path}/pdf_evidence/
  4. 复制 SKILL.md               → {vault}/{project_workspace_path}/SKILL.md
  5. 写 _vault_paths.md 索引到项目仓库 examples/{slug}-perspective/

不直接动用户已有的 Concepts / MOC / People 笔记 —— 那些用 update_vault_wikilinks.py 单独执行
（避免 sync 误覆盖手写内容）。

许可：MIT
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr); sys.exit(1)


def parse_config(config_path: Path) -> dict[str, Any]:
    text = config_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n([\s\S]+?)\n---", text)
    if not m:
        raise ValueError(f"{config_path} 缺少 YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}


def safe_copytree(src: Path, dst: Path, dry_run: bool = False) -> int:
    """递归复制 src 到 dst，dst 已存在则覆盖单个文件。返回拷贝文件数。"""
    if not src.exists():
        return 0
    if dry_run:
        return sum(1 for _ in src.rglob("*") if _.is_file())
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in src.rglob("*"):
        if f.is_file():
            rel = f.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Phase 5.5 Vault sync")
    ap.add_argument("--config", required=True,
                    help="_library_config.md 路径（含 v0.4.1 frontmatter）")
    ap.add_argument("--dry-run", action="store_true",
                    help="不实际复制，只打印计划")
    ap.add_argument("--prune", action="store_true",
                    help="按 examples_retention 策略瘦身项目仓库（不可逆，建议先确认 Vault 内容）")
    args = ap.parse_args()

    cfg = parse_config(Path(args.config).expanduser())

    project_repo = Path(cfg["project_repo_path"]).expanduser()
    example_path = project_repo / cfg["example_path"]
    vault_root = Path(cfg["vault_archive_path"]).expanduser()
    workspace_template = cfg.get("project_workspace_path", "Projects/scholar-wendao/{slug}")
    workspace = vault_root / workspace_template.format(slug=cfg["scholar_slug"])
    examples_retention = cfg.get("examples_retention", "lightweight")

    print(f"项目仓库 example: {example_path}", file=sys.stderr)
    print(f"Vault workspace:  {workspace}", file=sys.stderr)
    print(f"瘦身策略:         {examples_retention}", file=sys.stderr)
    print(f"dry-run:          {args.dry_run}", file=sys.stderr)
    print(file=sys.stderr)

    # === 1. references/research → {workspace}/research/ ===
    src = example_path / "references" / "research"
    dst = workspace / "research"
    n = safe_copytree(src, dst, args.dry_run)
    print(f"  research/    : {n} 文件 → {dst}", file=sys.stderr)

    # === 2. references/biography → {workspace}/biography/ ===
    src = example_path / "references" / "biography"
    dst = workspace / "biography"
    n = safe_copytree(src, dst, args.dry_run)
    print(f"  biography/   : {n} 文件 → {dst}", file=sys.stderr)

    # === 3. _pdf_evidence → {workspace}/pdf_evidence/ ===
    src = example_path / "_pdf_evidence"
    dst = workspace / "pdf_evidence"
    n = safe_copytree(src, dst, args.dry_run)
    print(f"  pdf_evidence/: {n} 文件 → {dst}", file=sys.stderr)

    # === 4. SKILL.md ===
    src = example_path / "SKILL.md"
    dst = workspace / "SKILL.md"
    if src.exists():
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"  SKILL.md     : 1 文件 → {dst}", file=sys.stderr)

    # === 5. 写 _vault_paths.md 索引到项目仓库 ===
    vault_paths_md = example_path / "_vault_paths.md"
    cards_dir = vault_root / cfg["library_cards_path"]
    files_dir = vault_root / cfg["library_files_path"]
    vault_paths_content = f"""# Vault Paths · {cfg.get('scholar_name_en', cfg.get('scholar_slug'))}

> 由 `scripts/sync_to_vault.py` 自动生成。指向用户 Vault 中本次蒸馏产物的真实位置。
> 项目仓库内 `examples/{cfg['scholar_slug']}-perspective/` 仅保留 SKILL.md 与本索引。

## 用户 Vault 内的真实素材路径

| 类别 | Vault 路径 |
| --- | --- |
| Library PDF 文件 | `{files_dir}` |
| Library Cards | `{cards_dir}` |
| 蒸馏工作区（research/biography/pdf_evidence） | `{workspace}` |
| 概念笔记 | `{vault_root / cfg['concepts_path']}` |
| 永久笔记（谱系） | `{vault_root / cfg['permanent_notes_path']}` |
| 主题地图（MOC） | `{vault_root / cfg['moc_path']}` |
| 人物志 | `{vault_root / cfg['people_path']}` |

## 配置

- `archive_layout`: `{cfg.get('archive_layout', 'flat')}`
- `examples_retention`: `{examples_retention}`
- `vault_archive_path`: `{vault_root}`

## 重新同步

如需重新跑 Vault 同步，从项目仓库执行：

```bash
python3 scripts/sync_to_vault.py \\
  --config {cfg['example_path']}/references/research/_library_config.md
```

`extract_pdf_evidence.py` + `generate_library_cards.py` 应当先于本脚本执行。
"""
    if not args.dry_run:
        vault_paths_md.write_text(vault_paths_content, encoding="utf-8")
    print(f"\n  _vault_paths.md → {vault_paths_md}", file=sys.stderr)

    # === 6. 项目仓库瘦身（依 examples_retention，需 --prune flag） ===
    if not args.prune:
        print(f"\n=== 瘦身跳过（默认）===", file=sys.stderr)
        print(f"  策略: {examples_retention}（用 --prune 执行）", file=sys.stderr)
        print(f"\n=== 完成 ===", file=sys.stderr)
        return

    print(f"\n=== 瘦身策略: {examples_retention} ===", file=sys.stderr)
    if examples_retention == "minimal":
        # 删除 references/ 和 _pdf_evidence/
        for sub in ["references", "_pdf_evidence"]:
            d = example_path / sub
            if d.exists():
                if not args.dry_run:
                    shutil.rmtree(d)
                print(f"  ✗ removed: {d}", file=sys.stderr)
    elif examples_retention == "lightweight":
        # 保留 references/research/ 和 _pdf_evidence/_navigator.md（含 _index/_concepts）
        # 删除 references/biography/ 和 _pdf_evidence/Stiegler*.md（仅留索引）
        bio = example_path / "references" / "biography"
        if bio.exists():
            if not args.dry_run:
                shutil.rmtree(bio)
            print(f"  ✗ removed: references/biography/ (副本在 Vault)", file=sys.stderr)
        # 保留 _pdf_evidence/_navigator.md / _index.json / _concepts.json，删除 *.md(其它)
        ev_dir = example_path / "_pdf_evidence"
        if ev_dir.exists():
            kept = {"_navigator.md", "_index.json", "_concepts.json"}
            removed = 0
            for f in ev_dir.glob("*.md"):
                if f.name not in kept:
                    if not args.dry_run:
                        f.unlink()
                    removed += 1
            print(f"  ✗ removed: _pdf_evidence/Stiegler*.md ({removed} 个,副本在 Vault)", file=sys.stderr)
    elif examples_retention == "full":
        print(f"  (全保留双份；不推荐,体积大)", file=sys.stderr)
    else:
        print(f"  ⚠️ 未知策略 '{examples_retention}',跳过瘦身", file=sys.stderr)

    print(f"\n=== 完成 ===", file=sys.stderr)


if __name__ == "__main__":
    main()
