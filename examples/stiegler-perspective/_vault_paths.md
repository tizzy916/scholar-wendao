# Vault Paths · Bernard Stiegler

> 由 `scripts/sync_to_vault.py` 自动生成。指向用户 Vault 中本次蒸馏产物的真实位置。
> 项目仓库内 `examples/stiegler-perspective/` 仅保留 SKILL.md 与本索引。

## 用户 Vault 内的真实素材路径

| 类别 | Vault 路径 |
| --- | --- |
| Library PDF 文件 | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/_files` |
| Library Cards | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Library 数字图书馆/Cards` |
| 蒸馏工作区（research/biography/pdf_evidence） | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Projects 项目/学者问道 Scholar-Wendao/Stiegler 蒸馏` |
| 概念笔记 | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Concepts 概念与理论` |
| 永久笔记（谱系） | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/Permanent Notes 永久笔记` |
| 主题地图（MOC） | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/MOC Maps 主题地图` |
| 人物志 | `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库/People 人物志` |

## 配置

- `archive_layout`: `flat`
- `examples_retention`: `lightweight`
- `vault_archive_path`: `/Users/shencong/Desktop/obsidian/tizzyVault/02 · Knowledge 知识库`

## 重新同步

如需重新跑 Vault 同步，从项目仓库执行：

```bash
python3 scripts/sync_to_vault.py \
  --config examples/stiegler-perspective/references/research/_library_config.md
```

`extract_pdf_evidence.py` + `generate_library_cards.py` 应当先于本脚本执行。
