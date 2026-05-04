#!/usr/bin/env python3
"""
biography_synth.py · 生平人格素材整合（带来源分级）

为 scholar-wendao 的 Phase 1 Agent 6 + Phase 2.7 服务：
  把分散的传记类素材（自传段落、访谈、传记、学生回忆）整合为
  结构化的 biography/ 目录，每条信息严格按 8 等级分级（A+ 到 C-）。

设计：
  本脚本不直接调用 LLM——它生成结构化的"提炼任务"prompt 文件 +
  接收 LLM 输出后规范化整合。这样设计的目的：

  1. 保留 agent 的完整推理过程（避免脚本过早压缩信息）
  2. 让来源分级的判断由 agent 在上下文中完成（脚本只检查格式）
  3. 不依赖任何 LLM API（学者问道是本地工具，不强制特定模型）

用法：
  # Step 1: 生成提炼任务
  python3 biography_synth.py --prepare --scholar "Bernard Stiegler" \\
    --raw-dir sources/biographies --out references/biography/

  # Step 2: agent 读取提炼任务，输出到指定文件
  # （agent 自动执行，无需手动）

  # Step 3: 验证 + 规范化
  python3 biography_synth.py --validate --dir references/biography/

许可：MIT
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 来源等级定义（与 references/extraction-framework.md §五一致）
SOURCE_GRADES = {
    "A+": "学者本人著作（出版）",
    "A": "学者本人长访谈（已出版/视频原始）",
    "A-": "学者本人讲座 transcript",
    "B+": "学者本人短文/书评/前言",
    "B": "同行评审论文中对学者的分析",
    "B-": "学位论文/会议论文",
    "C+": "已出版传记",
    "C": "学生/合作者回忆",
    "C-": "媒体报道/二手转述",
}

EXTRACTION_PROMPT_TEMPLATE = """\
# 提炼任务：{scholar} 的生平人格素材整合

> Phase 1 Agent 6 + Phase 2.7 任务。
> 为 ~/.claude/skills/{slug}-perspective/ 生成 biography/ 目录。

## 你的任务

阅读 `sources/biographies/` 目录下所有素材，整合为四份结构化文件：

1. `biography/timeline.md` - 结构化生平时间线
2. `biography/personality.md` - 性格特征（多源交叉验证）
3. `biography/relations.md` - 重要他者关系
4. `biography/controversies.md` - 重大争议与处世

## 严格遵守的规则

### 1. 每条信息必须标注来源等级（A+ 到 C-）

| 等级 | 含义 |
|---|---|
{grade_table}

### 2. 多源交叉验证强制

每条描述必须标注：
- 来源（具体文献，含页码）
- 等级
- 是否被多源（≥2 个独立来源）交叉验证

### 3. 区分"事实层"vs"叙事层"

❌ 错误："因为 X 经历，所以他后来 Y 思考"
✅ 正确：
   ```
   事实层：[年份] 学者在 [地点] 经历 [事件]（来源等级 C+，多源验证）
   叙事层：传记作者 X 认为这次经历影响了 [Y]
   判断说明：这是传记作者诠释。学者本人是否承认？
   ```

### 4. 警惕戏剧化形成性事件

对所有"戏剧性反转""监狱经历""突然顿悟"型故事特别警惕，
明确标注"叙事建构嫌疑"。

### 5. 隐私底线

不写入：
- 婚姻/家庭/子女（除非学者本人公开讨论 + 与学术工作直接相关）
- 性取向/健康/心理状态
- 政治倾向（除非是其学术工作核心）

## 输出格式

每个文件开头必须包含信息源声明（见下方模板）。

---

## 信息源声明模板

```markdown
# [文件名]

## 信息源声明

本文档采集时间：{date}
主要传记类来源：
- A 级（本人自述）：[列举]
- B 级（亲属/合作者/学生回忆）：[列举]
- C 级（传记作家/媒体）：[列举]

**警惕**：本文档涉及生平人格描写，**所有内容均带有不同程度的叙事建构**。
请理解这只是**用于辅助理解学者思想的语境**，**不是关于学者本人的事实陈述**。

---
```

## 字段约定（每条记录）

```markdown
### [事件/特征] · [简述]

**事实层**
- 时间：YYYY[-MM[-DD]]
- 地点：[如适用]
- 描述：[简述]
- 来源：[具体文献+页码]
- 等级：[A+ / A / ... / C-]
- 多源交叉：[是 / 否 / 部分（说明哪几条交叉）]

**叙事/诠释层**（如适用）
- [传记作者/学生/学者本人] 在 [何处] 如何叙述/诠释
- 与"事实层"的差异：[如有]

**判断说明**
- 是否有"戏剧化嫌疑"？[标注]
- 是否被多个独立来源交叉？[标注]
```

---

完成后运行：

```
python3 biography_synth.py --validate --dir references/biography/
```

确认所有条目符合格式与来源分级要求。
"""


def slugify(name: str) -> str:
    s = re.sub(r"\s+", "-", name.strip().lower())
    s = re.sub(r"[^a-z0-9\-]", "", s)
    return s


def prepare(scholar: str, raw_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    grade_table = "\n".join(f"| {k} | {v} |" for k, v in SOURCE_GRADES.items())
    slug = slugify(scholar)

    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        scholar=scholar,
        slug=slug,
        grade_table=grade_table,
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    prompt_path = out_dir / "_extraction_task.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    # 创建空的输出文件骨架（agent 将填充）
    for filename in ("timeline.md", "personality.md", "relations.md", "controversies.md"):
        path = out_dir / filename
        if not path.exists():
            path.write_text(
                f"# {filename.replace('.md', '').title()}\n\n"
                f"<!-- agent 将根据 _extraction_task.md 填充本文件 -->\n",
                encoding="utf-8",
            )

    raw_files = list(raw_dir.glob("**/*")) if raw_dir.exists() else []
    print(f"✓ 提炼任务已生成：{prompt_path}", file=sys.stderr)
    print(f"  原始素材目录：{raw_dir}（{len([f for f in raw_files if f.is_file()])} 个文件）", file=sys.stderr)
    print(f"\n下一步：让 agent 读取 _extraction_task.md 与 sources/biographies/，", file=sys.stderr)
    print(f"        并填充 timeline / personality / relations / controversies 四个文件。", file=sys.stderr)


# ===== 验证逻辑 =====

GRADE_PATTERN = re.compile(r"等级[:：]\s*\[?([ABC][+\-]?)\]?")
SOURCE_PATTERN = re.compile(r"来源[:：]\s*[\[「]?([^\]」\n]+)")
DATE_HEADER_PATTERN = re.compile(r"^##?#?\s+", re.MULTILINE)


def validate_file(path: Path) -> dict[str, Any]:
    """检查一个 biography 文件的合规性。"""
    text = path.read_text(encoding="utf-8")
    issues = []

    if "信息源声明" not in text:
        issues.append("缺少'信息源声明'章节")

    grades = GRADE_PATTERN.findall(text)
    sources = SOURCE_PATTERN.findall(text)
    sections = len(DATE_HEADER_PATTERN.findall(text))

    if sections > 0 and len(grades) == 0:
        issues.append("有条目但缺少等级标注（等级:A+/A/.../C-）")
    if sections > 0 and len(sources) == 0:
        issues.append("有条目但缺少来源标注（来源:文献+页码）")

    # 检查戏剧化嫌疑提示
    has_drama_warning = (
        "叙事建构" in text or "戏剧化" in text or "narrative" in text.lower()
    )
    if "因为" in text and "所以他" in text and not has_drama_warning:
        issues.append("可能存在线性因果叙事，未声明叙事建构警告")

    return {
        "file": str(path),
        "section_count": sections,
        "grade_count": len(grades),
        "grades_used": list(set(grades)),
        "source_count": len(sources),
        "issues": issues,
        "ok": not issues,
    }


def validate(dir_path: Path) -> None:
    files = ["timeline.md", "personality.md", "relations.md", "controversies.md"]
    results = []
    for f in files:
        p = dir_path / f
        if p.exists():
            results.append(validate_file(p))
        else:
            results.append({"file": str(p), "ok": False, "issues": ["文件不存在"]})

    all_ok = all(r["ok"] for r in results)

    print(f"=== 生平 biography 目录验证：{dir_path} ===", file=sys.stderr)
    for r in results:
        status = "✓" if r["ok"] else "✗"
        print(f"\n{status} {Path(r['file']).name}")
        if "section_count" in r:
            print(f"  条目数：{r['section_count']}, 等级标注：{r['grade_count']}, 来源标注：{r['source_count']}")
            print(f"  使用等级：{', '.join(sorted(r.get('grades_used', [])))}")
        if r["issues"]:
            print(f"  问题：")
            for issue in r["issues"]:
                print(f"    - {issue}")

    print(f"\n=== 验证{'通过' if all_ok else '不通过'} ===", file=sys.stderr)
    if not all_ok:
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="生平人格素材整合（含来源分级）")
    p.add_argument("--prepare", action="store_true", help="生成提炼任务给 agent")
    p.add_argument("--validate", action="store_true", help="验证 biography 目录的合规性")
    p.add_argument("--scholar", help="学者名（仅 --prepare 需要）")
    p.add_argument("--raw-dir", default="sources/biographies", help="原始传记素材目录")
    p.add_argument("--dir", default="references/biography", help="biography 目录")
    p.add_argument("-o", "--out", default="references/biography", help="输出目录（仅 --prepare）")
    args = p.parse_args()

    if args.prepare:
        if not args.scholar:
            p.error("--prepare 需要 --scholar")
        prepare(args.scholar, Path(args.raw_dir), Path(args.out))
    elif args.validate:
        validate(Path(args.dir))
    else:
        p.print_help()


if __name__ == "__main__":
    main()
