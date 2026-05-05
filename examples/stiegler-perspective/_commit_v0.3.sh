#!/usr/bin/env bash
# v0.3 提交脚本 · 在你的 macOS 终端中跑(沙箱无权写 .git/)
# 用法:cd ~/Desktop/scholar-wendao-skill && bash examples/stiegler-perspective/_commit_v0.3.sh

set -e

cd ~/Desktop/scholar-wendao-skill

# 清掉沙箱遗留的 lock(如有)
rm -f .git/index.lock 2>/dev/null
find .git/objects -name 'tmp_obj_*' -type f -delete 2>/dev/null

# Stiegler perspective skill 软链到 Claude Skills 目录
mkdir -p ~/.claude/skills
if [ -L ~/.claude/skills/stiegler-perspective ] || [ -d ~/.claude/skills/stiegler-perspective ]; then
  echo "⚠️  ~/.claude/skills/stiegler-perspective 已存在,跳过软链"
else
  ln -sfn ~/Desktop/scholar-wendao-skill/examples/stiegler-perspective \
    ~/.claude/skills/stiegler-perspective
  echo "✓ 软链:~/.claude/skills/stiegler-perspective → examples/stiegler-perspective"
fi

# git 操作
git add examples/

cat <<'COMMIT_MSG' > /tmp/v0.3_commit_msg.txt
v0.3: First validated example - Bernard Stiegler perspective skill

Distilled from 8 local primary PDFs (FR/EN/ZH) + 395 OpenAlex archive
records + 6 ground-truth Obsidian Concept notes cross-validation.

Concept map covers all 6 core Stiegler concepts (tertiary retention /
epiphylogenesis / pharmacology / general organology / symbolic misery /
proletarianization) + 3 secondary (grammatization / disruption /
neganthropy).

Static quality check: 100/100. Caricature test: PASS (80/100, revealed
term-density self-check necessity, now built into activation rules).

Information source composition: A+/A/A- (primary) ~70%, B (secondary)
~25%, C+/C (biographical) ~5%.

Honest boundaries: 5+1 statements (Polanyi tacit knowledge /
fossilization / public-vs-private / biographical rhetoric / caricature
/ suicide-respect-boundary). Includes explicit BRACKETING for
"prison-read-philosophy" narrative per biography-protocol.

Acquisition manifest: 46 closed-source books listed (24 fr Galilée +
16 en Polity + 6 und); ANNAS_API_KEY needed for live download.

Created by https://github.com/tizzy916/scholar-wendao-skill
COMMIT_MSG

git commit -F /tmp/v0.3_commit_msg.txt

git log --oneline -5
echo
echo "=== ready to push ==="
read -p "Push to GitHub origin/main? [y/N] " ans
if [[ "$ans" =~ ^[Yy]$ ]]; then
  git push origin main
  echo "✓ pushed v0.3"
else
  echo "(skipped push — run 'git push origin main' manually when ready)"
fi
