#!/usr/bin/env bash
# download_open_access.sh · 开放获取资源批量下载（v0.4）
#
# 读取 harvest_works.py 输出的 JSON，对所有 is_oa=true 的作品自动下载。
#
# v0.4 改进（基于 v0.3 实战 P2 #7 + P3 #9）：
#   1. 支持两种 archive_layout：
#      - flat（默认）：扁平命名 {prefix}{year}_{slug}[_{lang}].pdf 在 OUTPUT_DIR 根
#      - by-language：fr/en/zh 子目录（旧行为）
#   2. 跳过 doi.org 重定向链接（v0.3 实战中 doi.org 大概率把流量送进付费墙）；
#      改用 unpaywall API 解析真实 OA URL（需 UNPAYWALL_EMAIL 环境变量）
#   3. HTML 落地页检测：下载到 HTML 时尝试从中 grep 出 .pdf 直链重试
#   4. 详细失败日志 _failed.json：含 doi / title / url / reason
#
# 用法：
#   bash download_open_access.sh JSON_INPUT OUTPUT_DIR [ARCHIVE_LAYOUT] [PREFIX]
#   - ARCHIVE_LAYOUT: flat (默认) | by-language
#   - PREFIX: 文件名前缀（如 "Stiegler"），默认空字符串
#
# 例：
#   bash download_open_access.sh references/research/07-archive.json \
#       "$HOME/.../Library 数字图书馆/_files" flat Stiegler
#
# 依赖：jq, curl
#
# 环境变量：
#   UNPAYWALL_EMAIL   你的邮箱（unpaywall API 必需，免费）
#
# 许可：MIT

set -euo pipefail

JSON_INPUT="${1:-references/research/07-archive.json}"
OUTPUT_DIR="${2:-sources/works}"
ARCHIVE_LAYOUT="${3:-flat}"
PREFIX="${4:-}"

if [[ ! -f "$JSON_INPUT" ]]; then
    echo "ERROR: JSON 输入文件不存在: $JSON_INPUT" >&2
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: 缺少 jq。请安装：brew install jq" >&2
    exit 1
fi

if [[ "$ARCHIVE_LAYOUT" != "flat" && "$ARCHIVE_LAYOUT" != "by-language" ]]; then
    echo "ERROR: ARCHIVE_LAYOUT 必须是 'flat' 或 'by-language'，得到 '$ARCHIVE_LAYOUT'" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
FAILED_LOG="$OUTPUT_DIR/_failed.json"
SUCCESS_LOG="$OUTPUT_DIR/_downloaded.txt"
SKIPPED_LOG="$OUTPUT_DIR/_skipped.txt"
echo "[]" > "$FAILED_LOG.tmp"
: > "$SUCCESS_LOG"
: > "$SKIPPED_LOG"

SCHOLAR=$(jq -r '.scholar // "unknown"' "$JSON_INPUT")
echo "下载 ${SCHOLAR} 的开放获取作品（layout=$ARCHIVE_LAYOUT, prefix='${PREFIX}'）..."

TOTAL=$(jq '[.works[] | select(.is_oa == true and .oa_url != null)] | length' "$JSON_INPUT")
echo "共 ${TOTAL} 部 OA 作品待下载"
echo ""

COUNT=0
DOWNLOADED=0
SKIPPED=0
FAILED=0

# Helper: 给一个 URL，返回真实下载链接（doi.org → unpaywall API; 其他直接返回）
resolve_oa_url() {
    local url="$1"
    local doi=""
    if [[ "$url" == *"doi.org/"* ]]; then
        # 提取 DOI（doi.org/ 后面的部分）
        doi=$(echo "$url" | sed -E 's|.*doi\.org/||' | sed 's|^https?://||')
        if [[ -n "${UNPAYWALL_EMAIL:-}" ]]; then
            local resolved
            resolved=$(curl -sSf --max-time 15 \
                "https://api.unpaywall.org/v2/${doi}?email=${UNPAYWALL_EMAIL}" \
                2>/dev/null | jq -r '.best_oa_location.url_for_pdf // .best_oa_location.url // empty' || true)
            if [[ -n "$resolved" && "$resolved" != "null" ]]; then
                echo "$resolved"
                return 0
            fi
        fi
        # 没 unpaywall email 或没拿到结果 → 跳过 doi.org 链接
        echo ""
        return 1
    fi
    echo "$url"
    return 0
}

record_failure() {
    local title="$1" doi="$2" url="$3" reason="$4"
    # 增量追加到 _failed.json.tmp
    jq --arg t "$title" --arg d "$doi" --arg u "$url" --arg r "$reason" \
        '. += [{title: $t, doi: $d, url: $u, reason: $r}]' \
        "$FAILED_LOG.tmp" > "$FAILED_LOG.tmp.new" \
        && mv "$FAILED_LOG.tmp.new" "$FAILED_LOG.tmp"
}

while IFS=$'\t' read -r YEAR LANG TITLE URL FIRST_AUTHOR DOI; do
    COUNT=$((COUNT + 1))

    LAST_NAME=$(echo "$FIRST_AUTHOR" | awk '{print $NF}' | tr -dc 'A-Za-z')
    [[ -z "$LAST_NAME" ]] && LAST_NAME="anon"

    SAFE_TITLE=$(echo "$TITLE" \
        | tr -cd 'A-Za-z0-9 \-' \
        | tr ' ' '_' \
        | cut -c1-50)
    [[ -z "$SAFE_TITLE" ]] && SAFE_TITLE="untitled"

    [[ -z "$LANG" || "$LANG" == "null" ]] && LANG="und"

    # v0.4：根据 archive_layout 决定文件路径
    if [[ "$ARCHIVE_LAYOUT" == "flat" ]]; then
        # flat：{PREFIX}{YEAR}_{slug}[_{lang}].pdf 在 OUTPUT_DIR 根
        if [[ "$LANG" == "und" ]]; then
            FILENAME="${PREFIX}${YEAR}_${SAFE_TITLE}.pdf"
        else
            FILENAME="${PREFIX}${YEAR}_${SAFE_TITLE}_${LANG}.pdf"
        fi
        DEST="$OUTPUT_DIR/$FILENAME"
    else
        # by-language：旧的 fr/en/zh 子目录
        LANG_DIR="$OUTPUT_DIR/$LANG"
        mkdir -p "$LANG_DIR"
        FILENAME="${YEAR}_${LAST_NAME}_${SAFE_TITLE}.pdf"
        DEST="$LANG_DIR/$FILENAME"
    fi

    printf "[%d/%d] %s ... " "$COUNT" "$TOTAL" "$FILENAME" >&2

    if [[ -f "$DEST" ]]; then
        echo "已存在，跳过" >&2
        echo "$DEST" >> "$SKIPPED_LOG"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # v0.4：解析真实下载 URL（doi.org → unpaywall）
    REAL_URL=$(resolve_oa_url "$URL" || true)
    if [[ -z "$REAL_URL" ]]; then
        echo "跳过（doi.org 链接，未配 UNPAYWALL_EMAIL 或 API 无 OA）" >&2
        record_failure "$TITLE" "$DOI" "$URL" "doi_no_oa_resolved"
        FAILED=$((FAILED + 1))
        continue
    fi

    # 下载
    if ! curl -sSfL --connect-timeout 5 --max-time 120 --retry 2 \
        -A "scholar-wendao/0.4" \
        -o "$DEST.tmp" "$REAL_URL"; then
        echo "失败（HTTP 错误）" >&2
        record_failure "$TITLE" "$DOI" "$REAL_URL" "http_error"
        FAILED=$((FAILED + 1))
        continue
    fi

    SIZE=$(stat -f%z "$DEST.tmp" 2>/dev/null || stat -c%s "$DEST.tmp" 2>/dev/null || echo 0)

    # 检测是否真的是 PDF（首字节 %PDF）
    FIRST_BYTES=$(head -c 8 "$DEST.tmp" | xxd -p 2>/dev/null | tr -d '\n')
    if [[ "$FIRST_BYTES" =~ ^25504446 ]] && [[ "$SIZE" -ge 10240 ]]; then
        mv "$DEST.tmp" "$DEST"
        echo "OK ($((SIZE / 1024)) KB)" >&2
        echo "$DEST" >> "$SUCCESS_LOG"
        DOWNLOADED=$((DOWNLOADED + 1))
        continue
    fi

    # 看起来是 HTML 落地页 → 尝试 grep 出 .pdf 直链重试一次
    if grep -qE "\.pdf[\"']" "$DEST.tmp" 2>/dev/null; then
        # 提取第一个 .pdf 链接
        PDF_HREF=$(grep -oE 'href=["'\''][^"'\'']+\.pdf[^"'\'']*' "$DEST.tmp" \
            | head -1 | sed -E 's/^href=["'\'']//' || true)
        if [[ -n "$PDF_HREF" ]]; then
            # 处理相对 URL：取原 URL 的 scheme+host
            if [[ "$PDF_HREF" != http* ]]; then
                BASE=$(echo "$REAL_URL" | sed -E 's|^(https?://[^/]+).*|\1|')
                if [[ "$PDF_HREF" == /* ]]; then
                    PDF_URL="${BASE}${PDF_HREF}"
                else
                    PDF_URL="${BASE}/${PDF_HREF}"
                fi
            else
                PDF_URL="$PDF_HREF"
            fi

            rm -f "$DEST.tmp"
            if curl -sSfL --connect-timeout 5 --max-time 120 --retry 2 \
                -A "scholar-wendao/0.4" \
                -o "$DEST.tmp" "$PDF_URL"; then
                FIRST_BYTES2=$(head -c 8 "$DEST.tmp" | xxd -p 2>/dev/null | tr -d '\n')
                SIZE2=$(stat -f%z "$DEST.tmp" 2>/dev/null || stat -c%s "$DEST.tmp" 2>/dev/null || echo 0)
                if [[ "$FIRST_BYTES2" =~ ^25504446 ]] && [[ "$SIZE2" -ge 10240 ]]; then
                    mv "$DEST.tmp" "$DEST"
                    echo "OK via HTML fallback ($((SIZE2 / 1024)) KB)" >&2
                    echo "$DEST" >> "$SUCCESS_LOG"
                    DOWNLOADED=$((DOWNLOADED + 1))
                    continue
                fi
            fi
        fi
    fi

    # 都失败了
    rm -f "$DEST.tmp"
    if [[ "$SIZE" -lt 10240 ]]; then
        echo "失败（文件太小：${SIZE} bytes）" >&2
        record_failure "$TITLE" "$DOI" "$REAL_URL" "too_small_${SIZE}"
    else
        echo "失败（非 PDF 内容，疑落地页）" >&2
        record_failure "$TITLE" "$DOI" "$REAL_URL" "html_landing_page"
    fi
    FAILED=$((FAILED + 1))
done < <(jq -r '.works[]
  | select(.is_oa == true and .oa_url != null)
  | [.year, .language, (.title // "untitled"), .oa_url, (.coauthors[0] // "anon"), (.doi // "")]
  | @tsv' "$JSON_INPUT")

mv "$FAILED_LOG.tmp" "$FAILED_LOG"

echo ""
echo "=== 下载完成 ==="
echo "下载成功：$DOWNLOADED"
echo "已存在跳过：$SKIPPED"
echo "失败：$FAILED （详见 $FAILED_LOG）"
echo ""
if [[ "$FAILED" -gt 0 ]]; then
    echo "失败原因分布："
    jq -r '.[] | .reason' "$FAILED_LOG" | sort | uniq -c | sort -rn | sed 's/^/  /'
    echo ""
    echo "提示："
    echo "  - doi_no_oa_resolved: 设置 UNPAYWALL_EMAIL 环境变量后重试可解析"
    echo "  - html_landing_page: 出版商网站需登录或人工点击下载"
    echo "  - 真正闭源的，下一步用 annas_acquire.py 通过 Anna's Archive 获取"
fi
