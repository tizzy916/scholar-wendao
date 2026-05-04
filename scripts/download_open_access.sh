#!/usr/bin/env bash
# download_open_access.sh · 开放获取资源批量下载
#
# 读取 harvest_works.py 输出的 JSON，对所有 is_oa=true 的作品自动下载，
# 按语言分目录存到 sources/works/{lang}/ 下。
#
# 用法：
#   bash download_open_access.sh references/research/07-archive.json sources/works/
#
# 依赖：
#   - jq (brew install jq)
#   - curl
#
# 设计：
#   - 已下载的文件跳过（按文件名）
#   - 失败的记录到 _failed.txt，可单独重试
#   - 文件命名：{year}_{first-author-last-name}_{first-50-chars-of-title}.pdf
#
# 许可：MIT

set -euo pipefail

JSON_INPUT="${1:-references/research/07-archive.json}"
OUTPUT_DIR="${2:-sources/works}"

if [[ ! -f "$JSON_INPUT" ]]; then
    echo "ERROR: JSON 输入文件不存在: $JSON_INPUT" >&2
    echo "提示：先跑 harvest_works.py 生成档案" >&2
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: 缺少 jq。请安装：brew install jq" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
FAILED_LOG="$OUTPUT_DIR/_failed.txt"
SUCCESS_LOG="$OUTPUT_DIR/_downloaded.txt"
SKIPPED_LOG="$OUTPUT_DIR/_skipped.txt"
: > "$FAILED_LOG"
: > "$SUCCESS_LOG"
: > "$SKIPPED_LOG"

# 学者名（用于日志）
SCHOLAR=$(jq -r '.scholar' "$JSON_INPUT")
echo "下载 ${SCHOLAR} 的开放获取作品..."

# 拉出所有有 oa_url 的作品
TOTAL=$(jq '[.works[] | select(.is_oa == true and .oa_url != null)] | length' "$JSON_INPUT")
echo "共 ${TOTAL} 部 OA 作品待下载"
echo ""

COUNT=0
DOWNLOADED=0
SKIPPED=0
FAILED=0

# 用 jq 输出 tab 分隔的字段，方便 read 解析
jq -r '.works[]
  | select(.is_oa == true and .oa_url != null)
  | [.year, .language, (.title // "untitled"), .oa_url, (.coauthors[0] // "anon")]
  | @tsv' "$JSON_INPUT" | \
while IFS=$'\t' read -r YEAR LANG TITLE URL FIRST_AUTHOR; do
    COUNT=$((COUNT + 1))

    # 提取作者姓氏（最后一个词）
    LAST_NAME=$(echo "$FIRST_AUTHOR" | awk '{print $NF}' | tr -dc 'A-Za-z')
    [[ -z "$LAST_NAME" ]] && LAST_NAME="anon"

    # 标题清洗：取前 50 字符，去掉特殊符号
    SAFE_TITLE=$(echo "$TITLE" \
        | tr -cd 'A-Za-z0-9 \-' \
        | tr ' ' '_' \
        | cut -c1-50)
    [[ -z "$SAFE_TITLE" ]] && SAFE_TITLE="untitled"

    # 语言子目录
    [[ -z "$LANG" || "$LANG" == "null" ]] && LANG="und"
    LANG_DIR="$OUTPUT_DIR/$LANG"
    mkdir -p "$LANG_DIR"

    # 文件名
    FILENAME="${YEAR}_${LAST_NAME}_${SAFE_TITLE}.pdf"
    DEST="$LANG_DIR/$FILENAME"

    # 进度
    printf "[%d/%d] %s ... " "$COUNT" "$TOTAL" "$FILENAME" >&2

    # 跳过已下载
    if [[ -f "$DEST" ]]; then
        echo "已存在，跳过" >&2
        echo "$DEST" >> "$SKIPPED_LOG"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # 下载（5 秒连接超时，60 秒最长，最多 3 次重试）
    if curl -sSfL --connect-timeout 5 --max-time 60 --retry 3 \
        -A "scholar-wendao/0.2" \
        -o "$DEST.tmp" "$URL"; then
        # 简单验证：必须 >10KB 且不是 HTML
        SIZE=$(stat -f%z "$DEST.tmp" 2>/dev/null || stat -c%s "$DEST.tmp" 2>/dev/null || echo 0)
        if [[ "$SIZE" -lt 10240 ]]; then
            echo "失败（文件太小：${SIZE} bytes）" >&2
            rm -f "$DEST.tmp"
            echo "$URL" >> "$FAILED_LOG"
            FAILED=$((FAILED + 1))
            continue
        fi
        # 检查是否是 HTML 而非 PDF（一些站点会返回错误页）
        FIRST_BYTES=$(head -c 8 "$DEST.tmp" | xxd -p)
        if [[ "$FIRST_BYTES" =~ ^25504446 ]]; then  # %PDF
            mv "$DEST.tmp" "$DEST"
            echo "OK ($((SIZE / 1024)) KB)" >&2
            echo "$DEST" >> "$SUCCESS_LOG"
            DOWNLOADED=$((DOWNLOADED + 1))
        else
            echo "失败（非 PDF 内容）" >&2
            rm -f "$DEST.tmp"
            echo "$URL" >> "$FAILED_LOG"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "失败（HTTP 错误）" >&2
        echo "$URL" >> "$FAILED_LOG"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=== 下载完成 ==="
echo "下载成功：$DOWNLOADED"
echo "已存在跳过：$SKIPPED"
echo "失败：$FAILED （详见 $FAILED_LOG）"
echo ""
if [[ "$FAILED" -gt 0 ]]; then
    echo "提示：失败的链接可能是闭源伪标记或链接失效。"
    echo "对真正的闭源作品，下一步用 annas_acquire.py 通过 Anna's Archive 获取。"
fi
